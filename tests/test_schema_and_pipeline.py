from __future__ import annotations

from pathlib import Path

import pytest

from cemig_form_tool.models.schemas import ClientData
from cemig_form_tool.pipeline.orchestrator import FormPipeline
from cemig_form_tool.services.mapping_loader import MappingLoader


def test_mapping_schema_loads() -> None:
    mappings = MappingLoader().load(Path("configs/field_mapping.json"))
    assert mappings
    assert any(m.field_name == "full_name" for m in mappings)


def test_question_engine_for_missing_required_field() -> None:
    pipeline = FormPipeline()
    client = ClientData(full_name="Ana")
    q = pipeline.ask_next_question(client, ["full_name", "cpf_cnpj"], low_confidence_fields=[])
    assert q is not None
    assert q.field_name == "cpf_cnpj"

    pipeline.submit_answer(client, "cpf_cnpj", "12345678901")
    assert client.cpf_cnpj == "12345678901"


def test_workbook_inspector_detects_hidden_formula_and_locked(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    Workbook = openpyxl.Workbook

    from cemig_form_tool.services.workbook_inspector import WorkbookInspector

    wb = Workbook()
    ws = wb.active
    ws.title = "Formulário"
    ws["A1"] = "=1+1"
    ws["A2"].protection = ws["A2"].protection.copy(locked=True)
    hidden = wb.create_sheet("Dados")
    hidden.sheet_state = "hidden"
    path = tmp_path / "wb.xlsx"
    wb.save(path)

    report = WorkbookInspector().inspect(path)
    form = report["sheets"]["Formulário"]

    assert "Dados" in report["hidden_sheets"]
    assert "A1" in form.formula_cells
    assert "A2" in form.locked_cells
