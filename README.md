# CEMIG MicroGD Form Assistant

Python software to ingest client documents, extract/normalize data, ask human follow-up questions, and safely fill the CEMIG workbook template while preserving formulas, hidden sheets, validations, formatting, and merged cells.

## Current status
This repository now includes a modular baseline spanning the requested Phase 1/2/3 foundations:
- project structure and configuration
- document ingestion + extraction adapters (PDF/image/DOCX/TXT)
- field extraction and normalization scaffolding
- confidence filtering
- question engine
- workbook inspection and safe loader
- mapping loader and safe fill engine
- review/export layer (Excel + JSON)
- audit trail
- Streamlit skeleton with upload, preview, questions, review/export
- workbook preservation tests

## Architecture proposal

### Modules
- `config`: environment-driven settings
- `models`: pydantic schemas for data, mappings, Q&A, and audit entries
- `services.document_ingestion`: file type support and validation
- `services.text_extraction`: PDF/image/DOCX/TXT extraction adapters
- `services.field_extraction`: initial regex-based extraction scaffold
- `services.normalization`: CPF/CNPJ, phone, ZIP, email, state normalization hooks
- `services.confidence`: threshold split (accepted vs low-confidence)
- `services.question_engine`: asks required missing/low-confidence fields one-by-one
- `services.workbook_inspector`: formula/locked/editable/hidden sheet inspection
- `services.workbook_safe_loader`: safe template load/clone
- `services.mapping_loader`: YAML/JSON field mapping configuration
- `services.workbook_filler`: protected/formula-safe write logic
- `services.review_export`: review payload + xlsx/json exports
- `services.audit`: structured audit trail
- `pipeline.orchestrator`: service composition and workflow
- `ui.streamlit_app`: Streamlit app skeleton

## Workbook inspection strategy (safe)
1. Open with `openpyxl.load_workbook(data_only=False)`.
2. Enumerate all sheets and collect hidden states.
3. On `Formulário`, classify cells as:
   - formula cells (`value` starts with `=`)
   - protected/locked cells (`cell.protection.locked`)
   - editable candidates (empty + unlocked)
4. Preserve and validate data validation objects, merged ranges, formulas, and sheet visibility before/after writes.
5. Never write directly to formula or locked cells unless explicit mapping override is allowed.
6. Save to a new workbook output path only.

### Workbook template note
The file `Formulario-MicroGD_Rev_N4.xlsx` was not present in this environment. Use:

```bash
python scripts/inspect_workbook.py
```

to generate `configs/workbook_inspection_report.json` once the file is placed at repository root.

## Libraries and rationale
- `openpyxl`: safe Excel structure-preserving edits
- `pydantic`/`pydantic-settings`: typed models + environment config
- `pdfplumber` + `pypdf`: robust PDF text extraction fallback
- `python-docx`: DOCX parsing
- `pytesseract` + `Pillow`: OCR for scanned images/PDF-rendered images
- `PyYAML`: mapping config in YAML/JSON
- `streamlit`: fast human-in-the-loop UI
- `pytest`: regression tests for workbook integrity
- `rich` + `python-json-logger`: production-friendly logging

## Risks and mitigations
- **Template variability**: keep mapping externalized in YAML and versioned.
- **OCR noise**: confidence thresholds + mandatory follow-up questions.
- **Excel corruption risk**: strict no-write rules for formula/protected cells; preservation tests.
- **Low-confidence business-critical fields**: question engine prompts user instead of guessing.
- **Localization inconsistencies**: normalization utilities and validation hooks.

## Implementation phases
1. **Foundation (done baseline)**: structure, config, models, extraction adapters, workbook inspection/safe load, tests.
2. **Mapping and safe filling (done baseline)**: mapping loader, guarded write engine, per-answer workbook updates.
3. **UX/audit/export (done baseline)**: Streamlit flow, audit trail, JSON export, review step, printable/PDF strategy placeholder.

## Quick start (one command)

Use the helper script:

```bash
./run.sh all
```

Or run specific steps:

```bash
./run.sh setup
./run.sh test
./run.sh inspect
./run.sh app
```

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
streamlit run src/cemig_form_tool/ui/streamlit_app.py
```

## Project tree

```text
src/cemig_form_tool/
  config/
  models/
  pipeline/
  services/
  ui/
  utils/
configs/
  field_mapping.json
scripts/
  inspect_workbook.py
tests/
```

## Optional PDF strategy
Use a later adapter (e.g., WeasyPrint/reportlab/html-to-pdf) fed by the review JSON payload to generate a printable summary without altering the signed workbook flow.
