"""Review and export helpers."""

from __future__ import annotations

import json
from pathlib import Path

from openpyxl.workbook.workbook import Workbook

from cemig_form_tool.models.schemas import ClientData


class ReviewExportService:
    def build_review(self, data: ClientData, unanswered_required: list[str]) -> dict:
        return {
            "fields": data.model_dump(),
            "unanswered_required": unanswered_required,
            "ready_for_export": not unanswered_required,
        }

    def export_workbook(self, workbook: Workbook, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(output_path)
        return output_path

    def export_json(self, data: ClientData, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path
