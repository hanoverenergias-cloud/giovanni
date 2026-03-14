#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

usage() {
  cat <<'USAGE'
Usage: ./run.sh [command]

Commands:
  setup     Create venv and install project with dev dependencies
  test      Run pytest suite
  inspect   Run workbook inspection script
  app       Start Streamlit app
  all       Setup + test + inspect (default)
USAGE
}

ensure_venv() {
  if [[ ! -d "${VENV_DIR}" ]]; then
    echo "[run.sh] Creating virtual environment at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
  fi
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
}

setup() {
  ensure_venv
  echo "[run.sh] Installing dependencies"
  python -m pip install --upgrade pip
  pip install -e '.[dev]'
}

test_cmd() {
  ensure_venv
  pytest -q
}

inspect_cmd() {
  ensure_venv
  python scripts/inspect_workbook.py
}

app_cmd() {
  ensure_venv
  streamlit run src/cemig_form_tool/ui/streamlit_app.py
}

cmd="${1:-all}"

case "${cmd}" in
  setup)
    setup
    ;;
  test)
    test_cmd
    ;;
  inspect)
    inspect_cmd
    ;;
  app)
    app_cmd
    ;;
  all)
    setup
    test_cmd
    inspect_cmd
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown command: ${cmd}" >&2
    usage
    exit 1
    ;;
esac
