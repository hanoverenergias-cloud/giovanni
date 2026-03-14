from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cemig_form_tool.services.workbook_inspector import WorkbookInspector


def main() -> None:
    workbook = ROOT / "Formulario-MicroGD_Rev_N4.xlsx"
    report_path = ROOT / "configs/workbook_inspection_report.json"

    if not workbook.exists():
        report = {
            "workbook": str(workbook.name),
            "status": "missing",
            "message": "Workbook file not found in repository root.",
            "next_step": "Place the template in repo root and rerun python scripts/inspect_workbook.py",
        }
    else:
        inspection = WorkbookInspector().inspect(workbook, target_sheet="Formulário")
        serialized = {
            "sheet_names": inspection["sheet_names"],
            "hidden_sheets": inspection["hidden_sheets"],
            "warnings": inspection["warnings"],
            "sheets": {
                k: {
                    "sheet_name": v.sheet_name,
                    "hidden": v.hidden,
                    "formula_cells": v.formula_cells,
                    "locked_cells": v.locked_cells,
                    "editable_candidates": v.editable_candidates,
                }
                for k, v in inspection["sheets"].items()
            },
        }
        report = {"workbook": str(workbook.name), "status": "ok", "inspection": serialized}

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
