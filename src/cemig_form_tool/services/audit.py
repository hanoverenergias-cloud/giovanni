"""Audit trail management."""

from __future__ import annotations

import json
from pathlib import Path

from cemig_form_tool.models.schemas import AuditEntry


class AuditTrail:
    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    def add(self, action: str, detail: dict) -> None:
        self.entries.append(AuditEntry(action=action, detail=detail))

    def export_json(self, path: Path) -> None:
        payload = [entry.model_dump(mode="json") for entry in self.entries]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
