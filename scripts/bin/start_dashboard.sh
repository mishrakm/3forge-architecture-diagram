#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
LIVE_PORT="${LIVE_PORT:-8092}"
SERVE_DIR="${SERVE_DIR:-web}"
INSTANCES_CONFIG="${INSTANCES_CONFIG:-${ROOT_DIR}/instances.json}"
ADAPTER="${ADAPTER:-jdbc}"
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

cleanup() {
  local exit_code=$?
  if [[ -n "${STATIC_PID:-}" ]]; then
    kill "${STATIC_PID}" 2>/dev/null || true
  fi
  if [[ -n "${LIVE_PID:-}" ]]; then
    kill "${LIVE_PID}" 2>/dev/null || true
  fi
  wait 2>/dev/null || true
  exit "${exit_code}"
}

trap cleanup EXIT INT TERM

echo "Starting CORS server on ${HOST}:${PORT} for ${SERVE_DIR}..."
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/cors_server.py" --host "${HOST}" --port "${PORT}" --dir "${SERVE_DIR}" &
STATIC_PID=$!

echo "Starting live AMI server on ${HOST}:${LIVE_PORT} using ${INSTANCES_CONFIG}..."
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/live_view_server.py" \
  --host "${HOST}" \
  --port "${LIVE_PORT}" \
  --dir "${SERVE_DIR}" \
  --instances-config "${INSTANCES_CONFIG}" \
  --adapter "${ADAPTER}" &
LIVE_PID=$!

echo "Static docs: http://127.0.0.1:${PORT}/index.html"
echo "Live viewer: http://127.0.0.1:${LIVE_PORT}/ami_flow_live.html"

wait -n "${STATIC_PID}" "${LIVE_PID}"
