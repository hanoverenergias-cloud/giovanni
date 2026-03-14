"""Confidence scoring support."""

from __future__ import annotations

from cemig_form_tool.models.schemas import ExtractedField


class ConfidenceService:
    """Applies configurable confidence adjustments."""

    def apply_threshold(
        self,
        fields: list[ExtractedField],
        threshold: float,
    ) -> tuple[list[ExtractedField], list[ExtractedField]]:
        accepted = [f for f in fields if f.confidence >= threshold]
        low_confidence = [f for f in fields if f.confidence < threshold]
        return accepted, low_confidence
