"""End-to-end orchestration for extraction -> QA -> workbook fill."""

from __future__ import annotations

from pathlib import Path

from typing import Any

from cemig_form_tool.models.schemas import ClientData, Question
from cemig_form_tool.services.audit import AuditTrail
from cemig_form_tool.services.confidence import ConfidenceService
from cemig_form_tool.services.field_extraction import FieldExtractionService
from cemig_form_tool.services.mapping_loader import MappingLoader
from cemig_form_tool.services.normalization import NormalizationService
from cemig_form_tool.services.question_engine import QuestionEngine
from cemig_form_tool.services.text_extraction import TextExtractionPipeline
from cemig_form_tool.services.workbook_filler import WorkbookFiller


class FormPipeline:
    def __init__(self) -> None:
        self.extractor = TextExtractionPipeline()
        self.field_extractor = FieldExtractionService()
        self.normalizer = NormalizationService()
        self.confidence = ConfidenceService()
        self.questions = QuestionEngine()
        self.mapping_loader = MappingLoader()
        self.filler = WorkbookFiller()
        self.audit = AuditTrail()

    def ingest_documents(self, paths: list[Path], threshold: float) -> tuple[ClientData, list]:
        extracted = []
        for path in paths:
            text = self.extractor.extract_text(path)
            fields = self.field_extractor.extract(text, source_document=path.name)
            extracted.extend(fields)
            self.audit.add("document_processed", {"document": path.name, "fields_found": len(fields)})

        accepted, low_conf = self.confidence.apply_threshold(extracted, threshold)
        data = self.normalizer.to_client_data(accepted)
        self.audit.add(
            "extraction_finished",
            {"accepted": len(accepted), "low_confidence": len(low_conf)},
        )
        return data, low_conf

    def ask_next_question(
        self,
        client_data: ClientData,
        required_fields: list[str],
        low_confidence_fields: list,
    ) -> Question | None:
        question = self.questions.next_question(client_data, required_fields, low_confidence_fields)
        if question:
            self.audit.add("question_asked", question.model_dump(mode="json"))
        return question

    def submit_answer(self, client_data: ClientData, field_name: str, value: str) -> None:
        field = self.questions.register_answer(client_data, field_name, value)
        self.audit.add("question_answered", field.model_dump(mode="json"))

    def update_workbook(self, workbook: Any, mapping_path: Path, data: ClientData) -> list:
        mappings = self.mapping_loader.load(mapping_path)
        writes = self.filler.fill(workbook, data, mappings)
        self.audit.add("workbook_updated", {"writes": [w.model_dump(mode='json') for w in writes]})
        return writes
