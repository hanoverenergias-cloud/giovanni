"""Safe workbook filling engine with formula/protection checks."""

from __future__ import annotations

from typing import Any

from cemig_form_tool.models.schemas import ClientData, FieldMapping, WorkbookWriteRecord


class WorkbookFiller:
    def fill(self, workbook: Any, data: ClientData, mappings: list[FieldMapping]) -> list[WorkbookWriteRecord]:
        writes: list[WorkbookWriteRecord] = []
        for mapping in mappings:
            value = getattr(data, mapping.field_name, None)
            if value is None:
                continue

            ws = workbook[mapping.sheet]
            cell = ws[mapping.cell]

            if isinstance(cell.value, str) and cell.value.startswith("=") and not mapping.allow_formula_override:
                continue
            if cell.protection and cell.protection.locked:
                continue

            cell.value = value
            writes.append(
                WorkbookWriteRecord(
                    field_name=mapping.field_name,
                    sheet=mapping.sheet,
                    cell=mapping.cell,
                    value=str(value),
                )
            )

        return writes
