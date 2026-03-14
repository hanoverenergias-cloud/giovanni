"""Streamlit UI skeleton for phased workflow."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from cemig_form_tool.config.settings import settings
from cemig_form_tool.models.schemas import ClientData
from cemig_form_tool.pipeline.orchestrator import FormPipeline
from cemig_form_tool.services.review_export import ReviewExportService
from cemig_form_tool.services.workbook_safe_loader import WorkbookSafeLoader


def _ensure_state() -> None:
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = FormPipeline()
    if "client_data" not in st.session_state:
        st.session_state.client_data = ClientData()
    if "low_conf" not in st.session_state:
        st.session_state.low_conf = []
    if "workbook" not in st.session_state:
        st.session_state.workbook = None
    if "template_name" not in st.session_state:
        st.session_state.template_name = ""


def main() -> None:
    st.set_page_config(page_title="CEMIG Form Assistant", layout="wide")
    st.title("CEMIG MicroGD Form Assistant")
    _ensure_state()

    st.header("1) Upload documents")
    uploads = st.file_uploader("Upload PDF/Image/DOCX/TXT", accept_multiple_files=True)

    st.header("2) Load template workbook")
    template = st.file_uploader("Upload Formulario-MicroGD_Rev_N4.xlsx", type=["xlsx", "xlsm"])

    if st.button("Run extraction") and uploads:
        tmp_paths: list[Path] = []
        for file in uploads:
            path = Path("/tmp") / file.name
            path.write_bytes(file.getbuffer())
            tmp_paths.append(path)

        data, low_conf = st.session_state.pipeline.ingest_documents(
            tmp_paths,
            threshold=settings.confidence_threshold,
        )
        st.session_state.client_data = data
        st.session_state.low_conf = low_conf

    st.header("3) Extracted data preview")
    st.json(st.session_state.client_data.model_dump())

    required_fields = ["full_name", "cpf_cnpj", "installation_number", "city", "state"]
    question = st.session_state.pipeline.ask_next_question(
        st.session_state.client_data,
        required_fields=required_fields,
        low_confidence_fields=st.session_state.low_conf,
    )

    st.header("4) Question panel")
    if question:
        answer = st.text_input(question.prompt, key=f"answer_{question.field_name}")
        if st.button("Submit answer") and answer:
            st.session_state.pipeline.submit_answer(
                st.session_state.client_data,
                field_name=question.field_name,
                value=answer,
            )
            st.rerun()
    else:
        st.info("No pending required questions at the moment.")

    st.header("5) Review and export")
    review = ReviewExportService().build_review(st.session_state.client_data, unanswered_required=[])
    st.json(review)

    if template:
        if st.button("Prepare workbook"):
            template_path = Path("/tmp") / template.name
            template_path.write_bytes(template.getbuffer())
            st.session_state.template_name = template.name
            st.session_state.workbook = WorkbookSafeLoader().load_template(template_path)
            st.success("Workbook loaded safely.")

    if st.session_state.workbook and st.button("Apply mappings and export"):
        writes = st.session_state.pipeline.update_workbook(
            workbook=st.session_state.workbook,
            mapping_path=settings.mapping_file,
            data=st.session_state.client_data,
        )
        output_dir = settings.outputs_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        xlsx_path = output_dir / f"cemig_completed_{stamp}.xlsx"
        json_path = output_dir / f"cemig_completed_{stamp}.json"
        exporter = ReviewExportService()
        exporter.export_workbook(st.session_state.workbook, xlsx_path)
        exporter.export_json(st.session_state.client_data, json_path)
        st.success(f"Workbook exported with {len(writes)} writes: {xlsx_path}")
        st.caption(f"JSON exported: {json_path}")


if __name__ == "__main__":
    main()
