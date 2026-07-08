"""Contract PDF ingestion: extract raw text with PyMuPDF."""

import fitz


class EmptyPdfError(ValueError):
    """Raised when a PDF has no extractable text layer (e.g. scanned images)."""


def extract_text(pdf_bytes: bytes) -> str:
    """Return the concatenated text of every page of the contract."""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        pages = [page.get_text() for page in doc]
    text = "\n".join(pages).strip()
    if len(text) < 200:
        raise EmptyPdfError(
            "This PDF has little or no extractable text — it may be a "
            "scanned image. Please upload a text-based PDF."
        )
    return text
