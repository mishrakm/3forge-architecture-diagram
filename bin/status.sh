#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="${ROOT_DIR}/logs/live_view_server.pid"
PORT="${PORT:-18092}"

is_running() {
  local pid="$1"
  [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null
}

find_running_pid() {
  pgrep -f "scripts/live_view_server.py.*--port ${PORT}" | head -n 1 || true
}

if [[ -f "${PID_FILE}" ]]; then
  pid="$(<"${PID_FILE}")"
  if is_running "${pid}"; then
    echo "live_view_server is running (PID ${pid}, port ${PORT})."
    exit 0
  fi
  pid="$(find_running_pid)"
  if is_running "${pid}"; then
    mkdir -p "${ROOT_DIR}/logs"
    echo "${pid}" >"${PID_FILE}"
    echo "live_view_server is running (PID ${pid}, port ${PORT})."
    exit 0
  fi
  echo "live_view_server is not running, stale PID file found."
  exit 1
fi

pid="$(find_running_pid)"
if is_running "${pid}"; then
  mkdir -p "${ROOT_DIR}/logs"
  echo "${pid}" >"${PID_FILE}"
  echo "live_view_server is running (PID ${pid}, port ${PORT})."
  exit 0
fi

echo "live_view_server is not running."
exit 1