"""Normalization and validation helpers."""

from __future__ import annotations

import re

CPF_CNPJ_RE = re.compile(r"\D")
PHONE_RE = re.compile(r"\D")
ZIP_RE = re.compile(r"\D")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
STATE_CODES = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


def normalize_cpf_cnpj(value: str | None) -> str | None:
    if not value:
        return None
    digits = CPF_CNPJ_RE.sub("", value)
    if len(digits) in {11, 14}:
        return digits
    return None


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    digits = PHONE_RE.sub("", value)
    return digits if len(digits) >= 10 else None


def normalize_zip(value: str | None) -> str | None:
    if not value:
        return None
    digits = ZIP_RE.sub("", value)
    return digits if len(digits) == 8 else None


def normalize_state(value: str | None) -> str | None:
    if not value:
        return None
    state = value.strip().upper()
    return state if state in STATE_CODES else None


def is_valid_email(value: str | None) -> bool:
    return bool(value and EMAIL_RE.match(value.strip()))
