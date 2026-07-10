"""API surface tests — pipeline is stubbed, so no Azure/MongoDB needed."""

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from app import main
from app.ingest import EmptyPdfError
from app.schemas import ClauseReport, ClauseCategory, ComplianceReport, Verdict


def make_report(filename: str) -> ComplianceReport:
    return ComplianceReport(
        filename=filename,
        clauses=[
            ClauseReport(
                clause_type=ClauseCategory.probation,
                clause_text="Six months.",
                verdict=Verdict.compliant,
                citation="Labor Code, Art. 296 [281]",
                explanation="Within the six-month cap.",
            )
        ],
    )


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "analyze_contract", lambda data, name: make_report(name))
    monkeypatch.setattr(main, "analyze_text", lambda text, name: make_report(name))
    main._hits.clear()  # rate limiter is process-global
    return TestClient(main.app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_accepts_pdf(client):
    r = client.post("/analyze", files={"file": ("c.pdf", b"%PDF-1.4 fake", "application/pdf")})
    assert r.status_code == 200
    assert r.json()["filename"] == "c.pdf"
    assert r.json()["clauses"][0]["citation"]


def test_analyze_accepts_docx(client):
    r = client.post("/analyze", files={"file": ("c.docx", b"PK fake", "application/octet-stream")})
    assert r.status_code == 200


def test_analyze_rejects_unsupported_extension(client):
    r = client.post("/analyze", files={"file": ("photo.png", b"\x89PNG", "image/png")})
    assert r.status_code == 415


def test_analyze_rejects_oversized_upload(client, monkeypatch):
    monkeypatch.setattr(main, "MAX_BYTES", 1024)
    big = b"x" * 4096
    r = client.post("/analyze", files={"file": ("c.pdf", big, "application/pdf")})
    assert r.status_code == 413


def test_analyze_surfaces_unreadable_document(client, monkeypatch):
    def boom(data, name):
        raise EmptyPdfError("scanned image")

    monkeypatch.setattr(main, "analyze_contract", boom)
    r = client.post("/analyze", files={"file": ("c.pdf", b"%PDF", "application/pdf")})
    assert r.status_code == 422
    assert "scanned image" in r.json()["detail"]


def test_analyze_text_roundtrip(client):
    r = client.post("/analyze-text", json={"text": "x" * 200, "filename": "Pasted"})
    assert r.status_code == 200
    assert r.json()["filename"] == "Pasted"


def test_analyze_text_rejects_short_text(client, monkeypatch):
    def boom(text, name):
        raise EmptyPdfError("too short")

    monkeypatch.setattr(main, "analyze_text", boom)
    r = client.post("/analyze-text", json={"text": "hi"})
    assert r.status_code == 422


def test_rate_limit_blocks_after_quota(client, monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT", 2)
    main._hits.clear()
    payload = {"text": "x" * 200}
    assert client.post("/analyze-text", json=payload).status_code == 200
    assert client.post("/analyze-text", json=payload).status_code == 200
    r = client.post("/analyze-text", json=payload)
    assert r.status_code == 429


def test_report_always_carries_disclaimer(client):
    r = client.post("/analyze-text", json={"text": "x" * 200})
    assert "not legal advice" in r.json()["disclaimer"].lower()


def make_docx(paragraphs: list[str]) -> bytes:
    body = "".join(f"<w:p><w:r><w:t>{t}</w:t></w:r></w:p>" for t in paragraphs)
    doc = (
        '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org'
        f'/wordprocessingml/2006/main"><w:body>{body}</w:body></w:document>'
    )
    ct = (
        '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package'
        '/2006/content-types"><Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxml'
        'formats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    )
    rels = (
        '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org'
        '/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.'
        'openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc)
    return buf.getvalue()


def test_docx_extraction_roundtrip():
    from app.ingest import extract_text

    text = extract_text(
        make_docx(["EMPLOYMENT CONTRACT", "The Employee " + "shall comply. " * 20]),
        "c.docx",
    )
    assert "EMPLOYMENT CONTRACT" in text


def test_unsupported_extension_rejected_in_ingest():
    from app.ingest import extract_text

    with pytest.raises(EmptyPdfError):
        extract_text(b"data" * 100, "contract.png")
