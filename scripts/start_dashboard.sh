#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
PORT="${PORT:-8080}"
SERVE_DIR="${SERVE_DIR:-docs}"
PASSWORD="${AMI_DB_PASSWORD:-}"
SKIP_REFRESH="${SKIP_REFRESH:-0}"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Python executable not found at ${PYTHON_BIN}" >&2
  exit 1
fi

if [[ "${SKIP_REFRESH}" != "1" ]]; then
  if [[ -z "${PASSWORD}" ]]; then
    echo "Set AMI_DB_PASSWORD before running, or set SKIP_REFRESH=1 to serve existing docs." >&2
    exit 2
  fi

  echo "Refreshing docs from database..."
  AMI_DB_PASSWORD="${PASSWORD}" "${PYTHON_BIN}" "${ROOT_DIR}/scripts/document_tables.py"
else
  echo "Skipping DB refresh (SKIP_REFRESH=1)."
fi

echo "Starting CORS server on port ${PORT} for ${SERVE_DIR}..."
exec "${PYTHON_BIN}" "${ROOT_DIR}/scripts/cors_server.py" --port "${PORT}" --dir "${SERVE_DIR}"
