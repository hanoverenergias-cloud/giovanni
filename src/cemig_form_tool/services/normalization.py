"""Normalization orchestration from extracted fields to structured client data."""

from __future__ import annotations

from cemig_form_tool.models.schemas import ClientData, ExtractedField
from cemig_form_tool.utils.normalizers import (
    is_valid_email,
    normalize_cpf_cnpj,
    normalize_phone,
    normalize_state,
    normalize_zip,
)


class NormalizationService:
    def to_client_data(self, fields: list[ExtractedField]) -> ClientData:
        data: dict[str, object] = {}
        for item in fields:
            if item.name == "cpf_cnpj":
                data["cpf_cnpj"] = normalize_cpf_cnpj(item.value)
            elif item.name == "email" and is_valid_email(item.value):
                data["email"] = item.value
            elif item.name == "phone":
                data["phone"] = normalize_phone(item.value)
            elif item.name == "zip_code":
                data["zip_code"] = normalize_zip(item.value)
            elif item.name == "state":
                data["state"] = normalize_state(item.value)
            elif item.name in ClientData.model_fields:
                data[item.name] = item.value
        return ClientData(**data)
