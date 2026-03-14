"""Rule-based initial field extraction scaffold."""

from __future__ import annotations

import re

from cemig_form_tool.models.schemas import ExtractedField


class FieldExtractionService:
    """Simple baseline extractor; intended to be replaced by richer parser/LLM logic."""

    PATTERNS = {
        "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        "cpf_cnpj": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"),
        "zip_code": re.compile(r"\b\d{5}-?\d{3}\b"),
        "phone": re.compile(r"\(?\d{2}\)?\s?9?\d{4}-?\d{4}"),
    }

    def extract(self, text: str, source_document: str) -> list[ExtractedField]:
        results: list[ExtractedField] = []
        for field_name, pattern in self.PATTERNS.items():
            match = pattern.search(text)
            if match:
                results.append(
                    ExtractedField(
                        name=field_name,
                        value=match.group(0),
                        confidence=0.65,
                        source_document=source_document,
                        evidence=match.group(0),
                    )
                )
        return results
