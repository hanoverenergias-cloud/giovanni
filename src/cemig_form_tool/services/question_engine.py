"""Human-in-the-loop question engine."""

from __future__ import annotations

from cemig_form_tool.models.schemas import Answer, ClientData, DataOrigin, ExtractedField, Question


class QuestionEngine:
    """Determines missing or uncertain required fields and records responses."""

    def __init__(self) -> None:
        self.asked_fields: set[str] = set()
        self.answers: list[Answer] = []

    def next_question(
        self,
        client_data: ClientData,
        required_fields: list[str],
        low_confidence_fields: list[ExtractedField],
    ) -> Question | None:
        low_conf_map = {f.name for f in low_confidence_fields}
        for field_name in required_fields:
            value = getattr(client_data, field_name, None)
            if field_name in self.asked_fields:
                continue
            if value in (None, "") or field_name in low_conf_map:
                self.asked_fields.add(field_name)
                prompt = f"Please confirm the value for '{field_name.replace('_', ' ')}'."
                return Question(field_name=field_name, prompt=prompt)
        return None

    def register_answer(self, client_data: ClientData, field_name: str, value: str) -> ExtractedField:
        setattr(client_data, field_name, value)
        answer = Answer(field_name=field_name, value=value)
        self.answers.append(answer)
        return ExtractedField(name=field_name, value=value, confidence=1.0, origin=DataOrigin.MANUAL)
