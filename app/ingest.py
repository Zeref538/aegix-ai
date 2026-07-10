"""Contract ingestion: turn an uploaded file or pasted text into raw text.

Supported inputs:
  - PDF  (PyMuPDF)
  - DOCX (mammoth)
  - TXT  (decoded directly)
  - pasted plain text (used as-is)

Scanned/image-only documents have no text layer; we reject them and tell the
user to paste the text instead (there is no OCR step by design).
"""

import io
import os

import fitz

MIN_CHARS = 120


class EmptyPdfError(ValueError):
    """Raised when a document has no usable extractable text."""


def _pdf_text(data: bytes) -> str:
    with fitz.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc).strip()


def _docx_text(data: bytes) -> str:
    import mammoth

    return mammoth.extract_raw_text(io.BytesIO(data)).value.strip()


def extract_text(data: bytes, filename: str = "contract.pdf") -> str:
    """Extract text from an uploaded document, dispatching on its extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        text = _pdf_text(data)
    elif ext in (".docx", ".doc"):
        text = _docx_text(data)
    elif ext in (".txt", ".md", ".text"):
        text = data.decode("utf-8", errors="replace").strip()
    else:
        raise EmptyPdfError(
            "Unsupported file type. Upload a PDF, Word (.docx), or text file."
        )

    if len(text) < MIN_CHARS:
        raise EmptyPdfError(
            "Couldn't extract readable text from this file. If it's a scanned "
            "image, paste the contract text instead."
        )
    return text


def clean_pasted_text(text: str) -> str:
    """Validate and normalize contract text pasted directly by the user."""
    text = text.strip()
    if len(text) < MIN_CHARS:
        raise EmptyPdfError(
            "That looks too short to be a contract. Paste the full text "
            "(at least a few clauses)."
        )
    return text
