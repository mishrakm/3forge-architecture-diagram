#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="${ROOT_DIR}/logs/live_view_server.pid"
LOG_FILE="${ROOT_DIR}/logs/live_view_server.log"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-18092}"
SERVE_DIR="${SERVE_DIR:-web}"
INSTANCES_CONFIG="${INSTANCES_CONFIG:-instances.json}"
ADAPTER="${ADAPTER:-jdbc}"

if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${PYTHON_BIN:-${ROOT_DIR}/.venv/bin/python}"
elif command -v python3.13 >/dev/null 2>&1; then
  PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.13)}"
else
  PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"
fi

is_running() {
  local pid="$1"
  [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null
}

find_running_pid() {
  pgrep -f "scripts/live_view_server.py.*--port ${PORT}" | head -n 1 || true
}

if [[ -f "${PID_FILE}" ]]; then
  existing_pid="$(<"${PID_FILE}")"
  if is_running "${existing_pid}"; then
    echo "live_view_server is already running (PID ${existing_pid})."
    exit 0
  fi
  rm -f "${PID_FILE}"
fi

existing_pid="$(find_running_pid)"
if is_running "${existing_pid}"; then
  mkdir -p "${ROOT_DIR}/logs"
  echo "${existing_pid}" >"${PID_FILE}"
  echo "live_view_server is already running (PID ${existing_pid})."
  exit 0
fi

mkdir -p "${ROOT_DIR}/logs"

pushd "${ROOT_DIR}" >/dev/null
nohup "${PYTHON_BIN}" scripts/live_view_server.py \
  --host "${HOST}" \
  --port "${PORT}" \
  --dir "${SERVE_DIR}" \
  --instances-config "${INSTANCES_CONFIG}" \
  --adapter "${ADAPTER}" \
  >>"${LOG_FILE}" 2>&1 &
server_pid=$!
popd >/dev/null

echo "${server_pid}" >"${PID_FILE}"
echo "Started live_view_server (PID ${server_pid})"
echo "Log: ${LOG_FILE}"
