"""Text extraction adapters for PDF, image and DOCX documents."""

from __future__ import annotations

from pathlib import Path

from cemig_form_tool.models.schemas import DocumentType
from cemig_form_tool.services.document_ingestion import DocumentIngestionService


class TextExtractionPipeline:
    """Pluggable extraction pipeline with conservative fallbacks."""

    def __init__(self) -> None:
        self.ingestion = DocumentIngestionService()

    def extract_text(self, path: Path) -> str:
        doc_type = self.ingestion.classify(path)
        if doc_type == DocumentType.PDF:
            return self._extract_pdf(path)
        if doc_type == DocumentType.IMAGE:
            return self._extract_image(path)
        if doc_type == DocumentType.DOCX:
            return self._extract_docx(path)
        if doc_type == DocumentType.TXT:
            return path.read_text(encoding="utf-8", errors="ignore")
        return ""

    def _extract_pdf(self, path: Path) -> str:
        chunks: list[str] = []
        try:
            import pdfplumber

            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text() or ""
                    chunks.append(txt)
        except ModuleNotFoundError:
            pass

        if not "".join(chunks).strip():
            try:
                from pypdf import PdfReader
            except ModuleNotFoundError:
                return ""
            reader = PdfReader(str(path))
            for page in reader.pages:
                chunks.append(page.extract_text() or "")
        return "\n".join(chunks).strip()

    def _extract_image(self, path: Path) -> str:
        try:
            import pytesseract
            from PIL import Image
        except ModuleNotFoundError:
            return ""
        with Image.open(path) as img:
            return pytesseract.image_to_string(img)

    def _extract_docx(self, path: Path) -> str:
        try:
            from docx import Document
        except ModuleNotFoundError:
            return ""
        doc = Document(path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text).strip()
