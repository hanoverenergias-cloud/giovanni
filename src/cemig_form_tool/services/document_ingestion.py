"""Document ingestion service."""

from __future__ import annotations

from pathlib import Path

from cemig_form_tool.models.schemas import DocumentType


class DocumentIngestionService:
    """Classifies and registers uploaded documents."""

    SUPPORTED = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".txt"}

    def classify(self, path: Path) -> DocumentType:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return DocumentType.PDF
        if suffix in {".png", ".jpg", ".jpeg"}:
            return DocumentType.IMAGE
        if suffix == ".docx":
            return DocumentType.DOCX
        if suffix == ".txt":
            return DocumentType.TXT
        return DocumentType.UNKNOWN

    def validate_supported(self, path: Path) -> bool:
        return path.suffix.lower() in self.SUPPORTED
