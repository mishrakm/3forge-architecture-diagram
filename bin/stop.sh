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

if [[ ! -f "${PID_FILE}" ]]; then
  pid="$(find_running_pid)"
  if ! is_running "${pid}"; then
    echo "live_view_server is not running."
    exit 0
  fi
else
  pid="$(<"${PID_FILE}")"
fi

if ! is_running "${pid}"; then
  pid="$(find_running_pid)"
  if ! is_running "${pid}"; then
    rm -f "${PID_FILE}"
    echo "Removed stale PID file."
    exit 0
  fi
fi

echo "${pid}" >"${PID_FILE}"
kill "${pid}"
for _ in {1..20}; do
  if ! is_running "${pid}"; then
    rm -f "${PID_FILE}"
    echo "Stopped live_view_server (PID ${pid})."
    exit 0
  fi
done

kill -9 "${pid}"
rm -f "${PID_FILE}"
echo "Force stopped live_view_server (PID ${pid})."
