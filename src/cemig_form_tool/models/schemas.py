"""Core domain models for extraction, validation, Q&A and workbook mapping."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field as dc_field
from datetime import datetime
from enum import Enum
from typing import Any

try:  # pragma: no cover
    from pydantic import BaseModel, Field
except ModuleNotFoundError:  # pragma: no cover
    class BaseModel:  # type: ignore[override]
        model_fields: dict[str, Any] = {}

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            cls.model_fields = getattr(cls, "__annotations__", {})

        def model_dump(self, mode: str | None = None) -> dict[str, Any]:
            if hasattr(self, "__dataclass_fields__"):
                return asdict(self)
            return self.__dict__.copy()

    def Field(default: Any = None, **_: Any) -> Any:
        return default


class DataOrigin(str, Enum):
    DOCUMENT = "document"
    MANUAL = "manual"
    DERIVED = "derived"


class DocumentType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    DOCX = "docx"
    TXT = "txt"
    UNKNOWN = "unknown"


@dataclass
class ExtractedField(BaseModel):
    name: str
    value: str | None = None
    confidence: float = 0.0
    source_document: str | None = None
    evidence: str | None = None
    origin: DataOrigin = DataOrigin.DOCUMENT


@dataclass
class ClientData(BaseModel):
    full_name: str | None = None
    person_type: str | None = None
    cpf_cnpj: str | None = None
    rg_ie: str | None = None
    installation_number: str | None = None
    address: str | None = None
    neighborhood: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: str | None = None
    customer_classification: str | None = None
    request_type: str | None = None
    source_type: str | None = None
    compensation_modality: str | None = None
    installed_power_kw: float | None = None
    contracted_demand_kw: float | None = None
    fast_track: bool | None = None
    grid_zero: bool | None = None


@dataclass
class Question(BaseModel):
    field_name: str
    prompt: str
    asked_at: datetime = dc_field(default_factory=datetime.utcnow)


@dataclass
class Answer(BaseModel):
    field_name: str
    value: str
    answered_at: datetime = dc_field(default_factory=datetime.utcnow)


@dataclass
class FieldMapping(BaseModel):
    field_name: str
    sheet: str
    cell: str
    required: bool = False
    allow_formula_override: bool = False


@dataclass
class WorkbookWriteRecord(BaseModel):
    field_name: str
    sheet: str
    cell: str
    value: str
    timestamp: datetime = dc_field(default_factory=datetime.utcnow)


@dataclass
class AuditEntry(BaseModel):
    action: str
    detail: dict
    timestamp: datetime = dc_field(default_factory=datetime.utcnow)
