#!/usr/bin/env python3
"""Generate first-pass documentation for AMI DB tables using JDBC."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import itertools
import json
import os
import re
import secrets
import socket
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jaydebeapi
import jpype


DEFAULTS = {
    "adapter": "jdbc",
    "driver_class": "com.f1.ami.amidb.jdbc.AmiDbJdbcDriver",
    "url": "jdbc:amisql:125.125.126.5:3280",
    "user": "pwadmin",
    "jar_path": "./out.jar",
    "output_md": "./docs/generated/tables.md",
    "output_json": "./docs/generated/tables.json",
    "output_dashboard": "./web/tables_dashboard.html",
    "output_schema_md": "./docs/generated/schema_catalog.md",
    "output_schema_json": "./docs/generated/schema_catalog.json",
    "output_relationships_md": "./docs/generated/relationships.md",
    "output_relationships_json": "./docs/generated/relationships.json",
    "output_dataflow_md": "./docs/generated/data_flow.md",
    "output_dataflow_json": "./docs/generated/data_flow.json",
    "output_metrics_md": "./docs/generated/business_metrics.md",
    "output_metrics_json": "./docs/generated/business_metrics.json",
    "output_external_md": "./docs/generated/external_mappings.md",
    "output_external_json": "./docs/generated/external_mappings.json",
    "output_triggers_md": "./docs/generated/triggers.md",
    "output_triggers_json": "./docs/generated/triggers.json",
    "output_procedures_md": "./docs/generated/procedures.md",
    "output_procedures_json": "./docs/generated/procedures.json",
    "output_timers_md": "./docs/generated/timers.md",
    "output_timers_json": "./docs/generated/timers.json",
    "instances_config": "./instances.json",
    "output_multi_dashboard": "./web/ami_flow_viewer.html",
    "output_multi_json": "./docs/generated/ami_flow_viewer.json",
    "max_instances": 20,
    "telnet_timeout_sec": 6.0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AMI Flow Viewer generator for one or many AMI DB instances."
    )
    parser.add_argument(
        "--adapter",
        choices=["jdbc", "telnet"],
        default=os.getenv("AMI_DB_ADAPTER", DEFAULTS["adapter"]),
        help="Connection adapter: jdbc (default) or telnet.",
    )
    parser.add_argument("--driver-class", default=os.getenv("AMI_DB_DRIVER", DEFAULTS["driver_class"]))
    parser.add_argument("--url", default=os.getenv("AMI_DB_URL", DEFAULTS["url"]))
    parser.add_argument("--user", default=os.getenv("AMI_DB_USER", DEFAULTS["user"]))
    parser.add_argument("--password", default=os.getenv("AMI_DB_PASSWORD"))
    parser.add_argument("--jar-path", default=os.getenv("AMI_DB_JAR", DEFAULTS["jar_path"]))
    parser.add_argument(
        "--telnet-host",
        default=os.getenv("AMI_TELNET_HOST"),
        help="Telnet host. If omitted, host from --url may be used.",
    )
    parser.add_argument(
        "--telnet-port",
        type=int,
        default=int(os.getenv("AMI_TELNET_PORT", "0")) or None,
        help="Telnet port. If omitted, defaults to x290 when URL port is x280 (else URL port).",
    )
    parser.add_argument(
        "--telnet-login-command",
        default=os.getenv("AMI_TELNET_LOGIN_COMMAND", "Login"),
        help="Command prefix used to submit username, e.g. 'Login'.",
    )
    parser.add_argument(
        "--telnet-prompt",
        default=os.getenv("AMI_TELNET_PROMPT", ">"),
        help="Prompt marker used to detect command completion in telnet mode.",
    )
    parser.add_argument(
        "--telnet-timeout-sec",
        type=float,
        default=float(os.getenv("AMI_TELNET_TIMEOUT_SEC", str(DEFAULTS["telnet_timeout_sec"]))),
        help="Telnet read timeout in seconds (fail-fast for missing prompt/login).",
    )
    parser.add_argument("--output-md", default=DEFAULTS["output_md"])
    parser.add_argument("--output-json", default=DEFAULTS["output_json"])
    parser.add_argument("--output-dashboard", default=DEFAULTS["output_dashboard"])
    parser.add_argument("--output-schema-md", default=DEFAULTS["output_schema_md"])
    parser.add_argument("--output-schema-json", default=DEFAULTS["output_schema_json"])
    parser.add_argument(
        "--output-relationships-md", default=DEFAULTS["output_relationships_md"]
    )
    parser.add_argument(
        "--output-relationships-json", default=DEFAULTS["output_relationships_json"]
    )
    parser.add_argument("--output-dataflow-md", default=DEFAULTS["output_dataflow_md"])
    parser.add_argument(
        "--output-dataflow-json", default=DEFAULTS["output_dataflow_json"]
    )
    parser.add_argument("--output-metrics-md", default=DEFAULTS["output_metrics_md"])
    parser.add_argument("--output-metrics-json", default=DEFAULTS["output_metrics_json"])
    parser.add_argument("--output-external-md", default=DEFAULTS["output_external_md"])
    parser.add_argument("--output-external-json", default=DEFAULTS["output_external_json"])
    parser.add_argument("--output-triggers-md", default=DEFAULTS["output_triggers_md"])
    parser.add_argument("--output-triggers-json", default=DEFAULTS["output_triggers_json"])
    parser.add_argument("--output-procedures-md", default=DEFAULTS["output_procedures_md"])
    parser.add_argument("--output-procedures-json", default=DEFAULTS["output_procedures_json"])
    parser.add_argument("--output-timers-md", default=DEFAULTS["output_timers_md"])
    parser.add_argument("--output-timers-json", default=DEFAULTS["output_timers_json"])
    parser.add_argument(
        "--instances-config",
        default=None,
        help=(
            "Optional JSON file containing multiple instances. "
            "Format: either a list of instances or {\"instances\": [...]}"
        ),
    )
    parser.add_argument("--output-multi-dashboard", default=DEFAULTS["output_multi_dashboard"])
    parser.add_argument("--output-multi-json", default=DEFAULTS["output_multi_json"])
    parser.add_argument("--max-instances", type=int, default=DEFAULTS["max_instances"])
    parser.add_argument(
        "--java-home",
        default=os.getenv(
            "JAVA_HOME", "/usr/lib/jvm/java-17-openjdk-17.0.18.0.8-2.el9.x86_64"
        ),
        help="JAVA_HOME for starting the JVM.",
    )
    return parser.parse_args()


def ensure_jvm(java_home: str, classpath: list[str]) -> None:
    if jpype.isJVMStarted():
        return

    jvm_candidate = Path(java_home) / "lib" / "server" / "libjvm.so"
    if jvm_candidate.exists():
        jpype.startJVM(str(jvm_candidate), classpath=classpath)
        return

    java17_candidates = sorted(
        Path("/usr/lib/jvm").glob("java-17-openjdk*/lib/server/libjvm.so")
    )
    if java17_candidates:
        jpype.startJVM(str(java17_candidates[-1]), classpath=classpath)
        return

    # Fallback to the JVM detected by JPype when JAVA_HOME is stale.
    detected = jpype.getDefaultJVMPath()
    jpype.startJVM(detected, classpath=classpath)


def _extract_host_port(url: str) -> tuple[str | None, int | None]:
    if not url:
        return None, None
    if url.startswith("jdbc:"):
        parts = url.split(":")
        if len(parts) >= 2 and parts[-1].isdigit():
            return parts[-2], int(parts[-1])
    match = re.search(r"([^:/]+):(\d+)$", url)
    if match:
        return match.group(1), int(match.group(2))
    return None, None


def _derive_default_telnet_port(source_port: int | None) -> int | None:
    if source_port is None:
        return None
    # Common setup here: AMI DB on x280 and telnet shell on x290.
    if source_port % 100 == 80:
        return source_port + 10
    return source_port


def _parse_delimited(lines: list[str], delimiter: str) -> tuple[list[tuple[Any, ...]], list[tuple[str, ...]]]:
    if not lines:
        return [], []
    headers = [h.strip() for h in lines[0].split(delimiter)]
    rows: list[tuple[Any, ...]] = []
    for ln in lines[1:]:
        if not ln.strip():
            continue
        parts = [p.strip() for p in ln.split(delimiter)]
        if len(parts) < len(headers):
            parts += [""] * (len(headers) - len(parts))
        rows.append(tuple(parts[: len(headers)]))
    desc = [(h,) for h in headers]
    return rows, desc


def _parse_whitespace_table(lines: list[str]) -> tuple[list[tuple[Any, ...]], list[tuple[str, ...]]]:
    if not lines:
        return [], []
    header = [h.strip() for h in re.split(r"\s{2,}", lines[0].strip()) if h.strip()]
    if len(header) < 2:
        return [], []
    rows: list[tuple[Any, ...]] = []
    for ln in lines[1:]:
        if not ln.strip():
            continue
        parts = [p.strip() for p in re.split(r"\s{2,}", ln.strip())]
        if len(parts) < len(header):
            parts += [""] * (len(header) - len(parts))
        rows.append(tuple(parts[: len(header)]))
    return rows, [(h,) for h in header]


class TelnetAmiClient:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        *,
        login_command: str = "Login",
        prompt: str = ">",
        timeout_sec: float = 20.0,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.login_command = login_command
        self.prompt = prompt
        self.timeout_sec = timeout_sec
        self.sock = socket.create_connection((host, port), timeout=timeout_sec)
        self.sock.settimeout(timeout_sec)
        self._login()

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:  # noqa: BLE001
            pass

    def _send_line(self, text: str) -> None:
        self.sock.sendall((text + "\n").encode("utf-8", errors="ignore"))

    def _read_until_tokens(
        self,
        tokens: list[str],
        timeout_sec: float | None = None,
        *,
        allow_idle_on_data: bool = False,
        idle_grace_sec: float = 0.8,
    ) -> str:
        deadline = time.time() + (timeout_sec if timeout_sec is not None else self.timeout_sec)
        chunks: list[bytes] = []
        last_data_at: float | None = None
        while time.time() < deadline:
            try:
                data = self.sock.recv(4096)
            except TimeoutError:
                if allow_idle_on_data and chunks and last_data_at is not None:
                    if time.time() - last_data_at >= idle_grace_sec:
                        return b"".join(chunks).decode("utf-8", errors="ignore")
                continue
            if not data:
                break
            chunks.append(data)
            last_data_at = time.time()
            txt = b"".join(chunks).decode("utf-8", errors="ignore")
            txt_lower = txt.lower()
            if any(t.lower() in txt_lower for t in tokens):
                return txt
        text = b"".join(chunks).decode("utf-8", errors="ignore")
        tokens_joined = ", ".join(tokens)
        preview = text[-250:].replace("\n", " ").replace("\r", " ") if text else "<no data>"
        raise TimeoutError(
            f"Telnet timeout waiting for tokens [{tokens_joined}] from {self.host}:{self.port}. "
            f"Prompt/login may be incorrect. Last output: {preview}"
        )

    def _login(self) -> None:
        try:
            pre = self._read_until_tokens(
                ["login", "username", "password", self.prompt],
                timeout_sec=min(8.0, self.timeout_sec),
            )
        except TimeoutError:
            # Some endpoints don't print an initial banner/prompt; proceed by sending login command.
            pre = ""
        if "password" in pre.lower():
            self._send_line(self.password)
        elif self.prompt.lower() in pre.lower():
            # Already authenticated.
            return
        else:
            self._send_line(f"{self.login_command} {self.user}")
            pw_prompt = self._read_until_tokens(
                ["password", self.prompt],
                timeout_sec=min(8.0, self.timeout_sec),
            )
            if "password" in pw_prompt.lower():
                self._send_line(self.password)
        self._read_until_tokens(
            [self.prompt],
            timeout_sec=min(10.0, self.timeout_sec),
            allow_idle_on_data=True,
        )

    def execute(self, command: str) -> tuple[list[tuple[Any, ...]], list[tuple[str, ...]]]:
        self._send_line(command)
        raw = self._read_until_tokens(
            [self.prompt],
            timeout_sec=max(6.0, self.timeout_sec),
            allow_idle_on_data=True,
        )
        lines = [ln.rstrip("\r") for ln in raw.splitlines()]
        lines = [ln for ln in lines if ln.strip()]
        if lines and lines[0].strip().lower() == command.strip().lower():
            lines = lines[1:]
        lines = [ln for ln in lines if ln.strip() not in {self.prompt.strip(), self.prompt.strip() + " "}]
        if not lines:
            return [], []
        if lines[0].lower().startswith("error") or "exception" in lines[0].lower():
            raise RuntimeError(lines[0])
        if "\t" in lines[0]:
            return _parse_delimited(lines, "\t")
        if "|" in lines[0]:
            return _parse_delimited(lines, "|")
        if "," in lines[0] and (len(lines) == 1 or lines[1].count(",") == lines[0].count(",")):
            return _parse_delimited(lines, ",")
        ws_rows, ws_desc = _parse_whitespace_table(lines)
        if ws_rows or ws_desc:
            return ws_rows, ws_desc
        rows = [(ln,) for ln in lines]
        return rows, [("value",)]


class TelnetCursor:
    def __init__(self, client: TelnetAmiClient) -> None:
        self._client = client
        self._rows: list[tuple[Any, ...]] = []
        self.description: list[tuple[str, ...]] = []

    def execute(self, command: str) -> None:
        rows, desc = self._client.execute(command)
        self._rows = rows
        self.description = desc

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._rows

    def close(self) -> None:
        return


class TelnetConnection:
    def __init__(self, client: TelnetAmiClient) -> None:
        self._client = client

    def cursor(self) -> TelnetCursor:
        return TelnetCursor(self._client)

    def close(self) -> None:
        self._client.close()


def connect_db(
    adapter: str,
    driver_class: str,
    url: str,
    user: str,
    password: str,
    jar_path: str,
    java_home: str,
    telnet_host: str | None = None,
    telnet_port: int | None = None,
    telnet_login_command: str = "Login",
    telnet_prompt: str = ">",
    telnet_timeout_sec: float = 6.0,
) -> Any:
    if adapter == "telnet":
        host = telnet_host
        port = telnet_port
        if host is None or port is None:
            host2, port2 = _extract_host_port(url)
            host = host or host2
            port = port or _derive_default_telnet_port(port2)
        if not host or not port:
            raise ValueError(
                "Telnet adapter requires host/port in URL or explicit telnet settings."
            )
        client = TelnetAmiClient(
            host=host,
            port=port,
            user=user,
            password=password,
            login_command=telnet_login_command,
            prompt=telnet_prompt,
            timeout_sec=telnet_timeout_sec,
        )
        return TelnetConnection(client)

    jar_abs = str(Path(jar_path).resolve())
    if not Path(jar_abs).exists():
        raise FileNotFoundError(f"JDBC jar not found: {jar_abs}")

    ensure_jvm(java_home=java_home, classpath=[jar_abs])

    return jaydebeapi.connect(driver_class, url, [user, password])


def fetch_show_tables(cursor: Any) -> list[tuple[Any, ...]]:
    cursor.execute("show tables")
    rows = cursor.fetchall()
    rows = [r for r in rows if r and len(r) > 0 and not str(r[0]).startswith("__")]
    return sorted(rows, key=lambda row: str(row[0]).lower())


def fetch_table_schema(cursor: Any, table_name: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "table": table_name,
        "columns": [],
        "column_count": 0,
        "ddl": None,
        "errors": [],
    }

    try:
        cursor.execute(f"show table {table_name}")
        rows = cursor.fetchall()
        out["columns"] = [
            {
                "name": str(r[0]),
                "type": str(r[1]),
                "position": int(r[2]) if r[2] is not None else None,
                "nullable": bool(r[3]) if r[3] is not None else None,
                "index_mode": str(r[4]) if r[4] is not None else None,
            }
            for r in rows
        ]
        out["column_count"] = len(out["columns"])
    except Exception as exc:  # noqa: BLE001
        out["errors"].append(f"show table failed: {exc}")

    try:
        cursor.execute(f"describe table {table_name}")
        rows = cursor.fetchall()
        if rows:
            out["ddl"] = str(rows[0][0])
    except Exception as exc:  # noqa: BLE001
        out["errors"].append(f"describe table failed: {exc}")

    return out


def fetch_show_centers(cursor: Any) -> list[tuple[Any, ...]]:
    cursor.execute("show centers")
    return cursor.fetchall()


def fetch_show_replications(cursor: Any) -> list[tuple[Any, ...]]:
    cursor.execute("show replications")
    return cursor.fetchall()


def fetch_show_triggers(cursor: Any) -> list[tuple[Any, ...]]:
    cursor.execute("show triggers")
    return [r for r in cursor.fetchall() if r and len(r) > 0 and not str(r[0]).startswith("__")]


def fetch_show_procedures(cursor: Any) -> list[tuple[Any, ...]]:
    cursor.execute("show procedures")
    return [r for r in cursor.fetchall() if r and len(r) > 0 and not str(r[0]).startswith("__")]


def fetch_show_timers(cursor: Any) -> list[tuple[Any, ...]]:
    cursor.execute("show timers")
    return [r for r in cursor.fetchall() if r and len(r) > 0 and not str(r[0]).startswith("__")]


def fetch_show_datasources(cursor: Any) -> list[tuple[Any, ...]]:
    cursor.execute("show datasources")
    return cursor.fetchall()


def extract_trigger_use_option(text: str | None, key: str) -> str | None:
    if not text:
        return None
    pattern = re.compile(rf'{re.escape(key)}="([^"]+)"', re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1) if match else None


def fetch_trigger_details(cursor: Any, trigger_rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for row in trigger_rows:
        name = str(row[0])
        table_chain = str(row[1]) if row[1] is not None else ""
        object_type = str(row[2]) if row[2] is not None else None
        priority = str(row[3]) if row[3] is not None else None
        options_preview = str(row[4]) if row[4] is not None else None
        owner = str(row[5]) if row[5] is not None else None
        enabled = bool(row[6]) if row[6] is not None else None

        ddl = None
        ddl_error = None
        try:
            cursor.execute(f"describe trigger {name}")
            ddl_rows = cursor.fetchall()
            if ddl_rows:
                ddl = str(ddl_rows[0][0])
        except Exception as exc:  # noqa: BLE001
            ddl_error = str(exc)

        tables = [t.strip() for t in table_chain.split(",") if t and t.strip()]
        input_tables = tables[:-1] if len(tables) > 1 else tables
        output_table = tables[-1] if tables else None
        relay_source = ddl or options_preview
        relay_host = extract_trigger_use_option(relay_source, "host")
        relay_port = extract_trigger_use_option(relay_source, "port")

        details.append(
            {
                "name": name,
                "type": object_type,
                "priority": priority,
                "owner": owner,
                "enabled": enabled,
                "table_chain": tables,
                "input_tables": input_tables,
                "output_table": output_table,
                "relay_host": relay_host,
                "relay_port": relay_port,
                "options_preview": options_preview,
                "ddl": ddl,
                "ddl_error": ddl_error,
            }
        )

    details.sort(key=lambda x: x["name"].lower())
    return details


def derive_trigger_flows(trigger_details: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flows: list[dict[str, Any]] = []
    for trg in trigger_details:
        flows.append(
            {
                "trigger": trg["name"],
                "type": trg["type"],
                "input_tables": trg["input_tables"],
                "output_table": trg["output_table"],
                "relay_host": trg.get("relay_host"),
                "relay_port": trg.get("relay_port"),
                "enabled": trg["enabled"],
                "priority": trg["priority"],
            }
        )
    return flows


def fetch_procedure_details(cursor: Any, procedure_rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for row in procedure_rows:
        name = str(row[0])
        proc_type = str(row[1]) if len(row) > 1 and row[1] is not None else None
        return_type = str(row[2]) if len(row) > 2 and row[2] is not None else None
        arguments = str(row[3]) if len(row) > 3 and row[3] is not None else None
        options_preview = str(row[4]) if len(row) > 4 and row[4] is not None else None
        owner = str(row[5]) if len(row) > 5 and row[5] is not None else None

        ddl = None
        ddl_error = None
        try:
            cursor.execute(f"describe procedure {name}")
            ddl_rows = cursor.fetchall()
            if ddl_rows:
                ddl = str(ddl_rows[0][0])
        except Exception as exc:  # noqa: BLE001
            ddl_error = str(exc)

        details.append(
            {
                "name": name,
                "procedure_type": proc_type,
                "return_type": return_type,
                "arguments": arguments,
                "options_preview": options_preview,
                "owner": owner,
                "ddl": ddl,
                "ddl_error": ddl_error,
            }
        )

    details.sort(key=lambda x: x["name"].lower())
    return details


def fetch_timer_details(cursor: Any, timer_rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for row in timer_rows:
        name = str(row[0])
        timer_type = str(row[1]) if len(row) > 1 and row[1] is not None else None
        priority = str(row[2]) if len(row) > 2 and row[2] is not None else None
        schedule = str(row[3]) if len(row) > 3 and row[3] is not None else None
        options_preview = str(row[4]) if len(row) > 4 and row[4] is not None else None
        owner = str(row[5]) if len(row) > 5 and row[5] is not None else None
        last_run_time = str(row[6]) if len(row) > 6 and row[6] is not None else None
        next_run_time = str(row[7]) if len(row) > 7 and row[7] is not None else None
        enabled = bool(row[8]) if len(row) > 8 and row[8] is not None else None

        ddl = None
        ddl_error = None
        try:
            cursor.execute(f"describe timer {name}")
            ddl_rows = cursor.fetchall()
            if ddl_rows:
                ddl = str(ddl_rows[0][0])
        except Exception as exc:  # noqa: BLE001
            ddl_error = str(exc)

        details.append(
            {
                "name": name,
                "timer_type": timer_type,
                "priority": priority,
                "schedule": schedule,
                "options_preview": options_preview,
                "owner": owner,
                "last_run_time": last_run_time,
                "next_run_time": next_run_time,
                "enabled": enabled,
                "ddl": ddl,
                "ddl_error": ddl_error,
            }
        )

    details.sort(key=lambda x: x["name"].lower())
    return details


def build_table_records(rows: list[list[Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if len(row) < 9:
            continue
        is_realtime = row[1]
        if isinstance(is_realtime, int):
            is_realtime = bool(is_realtime)
        out.append(
            {
                "name": str(row[0]),
                "is_realtime": is_realtime,
                "initial_capacity": row[2],
                "storage_mode": row[3],
                "change_policy": row[4],
                "owner": row[5],
                "scope": row[6],
                "row_estimate": row[7],
                "column_count": row[8],
            }
        )
    return out


def infer_relationships(schemas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_column: dict[str, list[str]] = defaultdict(list)
    for schema in schemas:
        table = schema["table"]
        for col in schema.get("columns", []):
            name = str(col["name"]).lower()
            by_column[name].append(table)

    key_like = {
        "token",
        "traderid",
        "symbol",
        "pfno",
        "netbook",
        "acc",
        "user",
    }
    pair_scores: dict[tuple[str, str], set[str]] = defaultdict(set)

    for col, tables in by_column.items():
        unique_tables = sorted(set(tables))
        if len(unique_tables) < 2:
            continue
        is_keyish = col.endswith("id") or col in key_like
        if not is_keyish:
            continue
        if len(unique_tables) > 12:
            continue
        for left, right in itertools.combinations(unique_tables, 2):
            pair_scores[(left, right)].add(col)

    relationships = [
        {
            "left_table": pair[0],
            "right_table": pair[1],
            "shared_keys": sorted(cols),
            "strength": len(cols),
        }
        for pair, cols in pair_scores.items()
    ]
    relationships.sort(key=lambda x: (-x["strength"], x["left_table"], x["right_table"]))
    return relationships


def classify_data_flow(
    table_records: list[dict[str, Any]], schemas: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    existing = {t["name"] for t in table_records}
    schema_by_name = {s["table"]: s for s in schemas}
    out: list[dict[str, Any]] = []

    for table in table_records:
        name = table["name"]
        n = name.lower()
        owner = str(table.get("owner") or "").upper()
        storage_mode = str(table.get("storage_mode") or "").upper()
        is_realtime = table.get("is_realtime") is True

        if owner in {"SYSTEM", "AMI"}:
            category = "system"
        elif storage_mode == "HISTORICAL":
            category = "source_historical"
        elif any(k in n for k in ["agg", "summary", "group", "delta", "snap", "result"]):
            category = "derived_aggregate"
        elif is_realtime:
            category = "streaming_live"
        else:
            category = "core_operational"

        base_name = re.sub(r"^u\d+_", "", n)
        base_name = re.sub(r"(aggc\d+|agg|summary|grouped|delta|snap|filtered)$", "", base_name)
        upstream_hints = sorted(
            t
            for t in existing
            if t.lower() != n and (base_name and base_name in t.lower())
        )[:6]

        schema = schema_by_name.get(name, {})
        columns = [c["name"] for c in schema.get("columns", [])]
        out.append(
            {
                "table": name,
                "category": category,
                "owner": table.get("owner"),
                "storage_mode": table.get("storage_mode"),
                "is_realtime": table.get("is_realtime"),
                "column_count": len(columns),
                "upstream_hints": upstream_hints,
            }
        )

    out.sort(key=lambda x: (x["category"], x["table"].lower()))
    return out


def infer_business_metrics(schemas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    numeric_types = {"integer", "long", "float", "double", "short", "byte", "decimal"}
    out: list[dict[str, Any]] = []

    for schema in schemas:
        table = schema["table"]
        columns = schema.get("columns", [])
        cols_lower = {str(c["name"]).lower(): c for c in columns}
        numeric_cols = [
            c["name"]
            for c in columns
            if str(c.get("type", "")).lower() in numeric_types
        ]

        suggestions: list[dict[str, str]] = []

        if "buyqty" in cols_lower and "sellqty" in cols_lower:
            suggestions.append(
                {
                    "metric": "turnover_qty",
                    "formula_hint": "BuyQty + SellQty",
                }
            )
        if "buyvalue" in cols_lower and "sellvalue" in cols_lower:
            suggestions.append(
                {
                    "metric": "turnover_value",
                    "formula_hint": "BuyValue + SellValue",
                }
            )
        if "buyvalue" in cols_lower and "sellvalue" in cols_lower and "bexpense" in cols_lower and "sexpense" in cols_lower:
            suggestions.append(
                {
                    "metric": "net_trade_pnl",
                    "formula_hint": "SellValue - BuyValue - BExpense - SExpense",
                }
            )
        if any("pnl" in str(c["name"]).lower() for c in columns):
            pnl_cols = [c["name"] for c in columns if "pnl" in str(c["name"]).lower()]
            suggestions.append(
                {
                    "metric": "pnl_reported",
                    "formula_hint": f"Use existing pnl columns: {', '.join(pnl_cols)}",
                }
            )
        if "netbook" in cols_lower and "symbol" in cols_lower:
            suggestions.append(
                {
                    "metric": "net_position_by_symbol",
                    "formula_hint": "Aggregate by Symbol, NetBook",
                }
            )

        if suggestions:
            out.append(
                {
                    "table": table,
                    "numeric_columns": numeric_cols,
                    "suggested_metrics": suggestions,
                }
            )

    out.sort(key=lambda x: x["table"].lower())
    return out


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    rows = payload["rows"]
    generated_at = payload["generated_at_utc"]
    query = payload["query"]

    lines = [
        "# Database Tables",
        "",
        f"Generated at (UTC): {generated_at}",
        "",
        "## Source",
        "",
        f"- URL: {payload['url']}",
        f"- User: {payload['user']}",
        f"- Driver: {payload['driver_class']}",
        f"- Query: `{query}`",
        "",
        "## Summary",
        "",
        f"- Total tables: {len(rows)}",
        "",
        "## Tables",
        "",
        "| Table Name | Raw Metadata |",
        "|---|---|",
    ]

    for row in rows:
        table_name = str(row[0])
        raw = json.dumps(list(row), ensure_ascii=True)
        lines.append(f"| {table_name} | `{raw}` |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_dashboard(
        path: Path,
        payload: dict[str, Any],
        logic_payload: dict[str, Any],
) -> None:
        table_rows = payload["rows"]
        dashboard_data = {
                "generated_at_utc": payload["generated_at_utc"],
                "url": payload["url"],
                "user": payload["user"],
                "driver_class": payload["driver_class"],
                "tables": [
                        {
                                "name": row[0],
                                "is_realtime": bool(row[1]) if row[1] is not None else None,
                                "limit": row[2],
                                "storage_mode": row[3],
                                "change_policy": row[4],
                                "owner": row[5],
                                "scope": row[6],
                                "row_estimate": row[7],
                                "column_count": row[8],
                        }
                        for row in table_rows
                ],
                "schemas": logic_payload["schemas"],
                "relationships": logic_payload["relationships"],
                "data_flow": logic_payload["data_flow"],
                "business_metrics": logic_payload["business_metrics"],
                "external_mappings": logic_payload["external_mappings"],
                "trigger_flows": logic_payload["trigger_flows"],
                "procedure_details": logic_payload["procedure_details"],
                "timer_details": logic_payload["timer_details"],
        }
        dashboard_json = json.dumps(dashboard_data, ensure_ascii=True)

        html = """<!doctype html>
        <html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>AMI Flow Viewer</title>
    <style>
        :root {
            --bg: #f2efe9;
            --card: #ffffff;
            --ink: #2a2723;
            --muted: #67615b;
            --line: #e6ddd1;
            --primary: #0d6f8b;
            --accent: #b8582d;
            --shadow: 0 10px 24px rgba(20, 18, 15, 0.08);
        }

        * { box-sizing: border-box; }
        body {
            margin: 0;
            color: var(--ink);
            font-family: "Segoe UI", Tahoma, sans-serif;
            background:
                radial-gradient(1200px 500px at 0% 0%, #d7eef580, transparent),
                radial-gradient(900px 500px at 100% 0%, #f5d9cc70, transparent),
                var(--bg);
        }

        .wrap { max-width: 1280px; margin: 0 auto; padding: 20px; }
        .hero {
            border-radius: 16px;
            background: linear-gradient(135deg, #0d6f8b, #0a596f);
            color: #fff;
            padding: 20px;
            box-shadow: var(--shadow);
        }
        .hero h1 { margin: 0 0 8px; font-size: 30px; }
        .hero p { margin: 4px 0; opacity: 0.94; }

        .kpis { margin-top: 14px; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }
        .card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 12px;
            box-shadow: var(--shadow);
        }
        .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.7px; }
        .value { margin-top: 6px; font-size: 24px; font-weight: 700; }

        .tabs { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 8px; }
        .tab-btn {
            border: 1px solid var(--line);
            background: #fff;
            color: var(--ink);
            padding: 8px 12px;
            border-radius: 999px;
            cursor: pointer;
            font-weight: 600;
        }
        .tab-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }

        .panel { margin-top: 12px; display: none; }
        .panel.active { display: block; }
        .panel .toolbar { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }

        input, select {
            height: 36px;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 0 10px;
            background: #fff;
            min-width: 180px;
        }

        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .bar-row { display: grid; grid-template-columns: 130px 1fr 44px; gap: 8px; align-items: center; margin: 8px 0; }
        .bar-name { color: var(--muted); font-size: 12px; }
        .bar-wrap { height: 10px; background: #f1ece4; border-radius: 999px; overflow: hidden; }
        .bar { height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent)); }
        .bar-num { text-align: right; font-size: 12px; font-weight: 700; }

        table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid var(--line);
            border-radius: 12px;
            overflow: hidden;
            background: #fff;
        }
        th, td { border-bottom: 1px solid #f3ede4; padding: 9px; font-size: 12px; text-align: left; vertical-align: top; }
        th { background: #f9f6f1; position: sticky; top: 0; z-index: 1; }
        .table-wrap { max-height: 66vh; overflow: auto; border-radius: 12px; }
        .muted { color: var(--muted); font-size: 12px; }
        .pill { display:inline-block; border:1px solid #cde2ea; background:#edf7fb; color:#145367; border-radius:999px; padding:2px 8px; font-size:11px; }
        .lineage-wrap { border: 1px solid var(--line); border-radius: 12px; background: #fbfaf7; overflow: auto; }
        .lineage-svg { min-width: 760px; width: 100%; display: block; }
        .lineage-node-table { fill: #f6ede2; stroke: #d9b585; stroke-width: 1; }
        .lineage-node-trigger { fill: #dff1f7; stroke: #7fb1c4; stroke-width: 1; }
        .lineage-edge { stroke: #8f8a84; stroke-width: 1.2; fill: none; marker-end: url(#arrow); opacity: 0.9; }
        .lineage-label { font-size: 11px; fill: #2a2723; dominant-baseline: middle; }
        .lineage-label-tspan { dominant-baseline: central; }
        .lineage-legend { margin-top: 8px; font-size: 12px; color: var(--muted); }

        @media (max-width: 1000px) {
            .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class=\"wrap\">
        <section class=\"hero\">
            <h1>AMI Flow Viewer</h1>
            <p id=\"source\"></p>
            <p id=\"generated\"></p>
        </section>

        <section class=\"kpis\" id=\"kpis\"></section>

        <section class=\"tabs\">
            <button class=\"tab-btn active\" data-tab=\"triggers\">Trigger Flow</button>
            <button class=\"tab-btn\" data-tab=\"tables\">Tables</button>
            <button class=\"tab-btn\" data-tab=\"schema\">Schema</button>
            <button class=\"tab-btn\" data-tab=\"relationships\">Relationships</button>
            <button class=\"tab-btn\" data-tab=\"dataflow\">Data Flow</button>
            <button class=\"tab-btn\" data-tab=\"metrics\">Metrics</button>
            <button class=\"tab-btn\" data-tab=\"procedures\">Procedures</button>
            <button class=\"tab-btn\" data-tab=\"timers\">Timers</button>
            <button class="tab-btn" data-tab="external">External Mappings</button>
        </section>

        <section class=\"panel\" id=\"panel-tables\">
            <div class=\"grid\">
                <div class=\"card\"><h3>Tables by Owner</h3><div id=\"ownerBars\"></div></div>
                <div class=\"card\"><h3>Largest by Row Estimate</h3><div id=\"largestBars\"></div></div>
            </div>
            <div class=\"card\" style=\"margin-top:10px;\">
                <div class=\"toolbar\">
                    <input id=\"tableSearch\" placeholder=\"Search table\">
                    <select id=\"ownerFilter\"></select>
                    <select id=\"policyFilter\"></select>
                </div>
                <p class=\"muted\" id=\"tableCount\"></p>
                <div class=\"table-wrap\"><table><thead><tr><th>Table</th><th>Owner</th><th>Policy</th><th>Scope</th><th>Rows</th><th>Cols</th><th>Realtime</th></tr></thead><tbody id=\"tableRows\"></tbody></table></div>
            </div>
        </section>

        <section class="panel" id="panel-schema">
            <div class=\"card\">
                <div class=\"toolbar\"><input id=\"schemaSearch\" placeholder=\"Search table/column\"></div>
                <p class=\"muted\" id=\"schemaCount\"></p>
                <div class=\"table-wrap\"><table><thead><tr><th>Table</th><th>Column</th><th>Type</th><th>Nullable</th><th>Index</th></tr></thead><tbody id=\"schemaRows\"></tbody></table></div>
            </div>
        </section>
        <section class="panel" id="panel-external">
            <div class="card">
                <h3>Centers</h3>
                <p class="muted" id="centerCount"></p>
                <div class="table-wrap"><table><thead><tr><th>Name</th><th>Address</th><th>Status</th><th>Peers</th><th>Rows</th></tr></thead><tbody id="centerRows"></tbody></table></div>
            </div>
            <div class="card" style="margin-top:10px;">
                <h3>Replications</h3>
                <p class="muted" id="replCount"></p>
                <div class="table-wrap"><table><thead><tr><th>Name</th><th>Target</th><th>Source Center</th><th>Source Table</th><th>Rows</th><th>Status</th></tr></thead><tbody id="replRows"></tbody></table></div>
            </div>
        </section>
        <section class="panel active" id="panel-triggers">
            <div class="card">
                <h3>Trigger Input -> Output Flow</h3>
                <p class="muted" id="triggerCount"></p>
                <div class="table-wrap"><table><thead><tr><th>Trigger</th><th>Type</th><th>Inputs</th><th>Output</th><th>Enabled</th><th>Priority</th></tr></thead><tbody id="triggerRows"></tbody></table></div>
            </div>
            <div class="card" style="margin-top:10px;">
                <h3>Compact Lineage Graph</h3>
                <p class="muted" id="lineageSummary"></p>
                <div class="lineage-wrap">
                    <svg id="lineageGraph" class="lineage-svg" viewBox="0 0 760 320" preserveAspectRatio="xMidYMin meet"></svg>
                </div>
                <div class="lineage-legend">Left: source tables | Middle: triggers | Right: target tables</div>
            </div>
        </section>

        <section class=\"panel\" id=\"panel-relationships\">
            <div class=\"card\">
                <div class=\"toolbar\"><input id=\"relSearch\" placeholder=\"Search table/key\"></div>
                <p class=\"muted\" id=\"relCount\"></p>
                <div class=\"table-wrap\"><table><thead><tr><th>Left</th><th>Right</th><th>Shared Keys</th><th>Strength</th></tr></thead><tbody id=\"relRows\"></tbody></table></div>
            </div>
        </section>

        <section class=\"panel\" id=\"panel-dataflow\">
            <div class=\"card\">
                <div class=\"toolbar\"><input id=\"flowSearch\" placeholder=\"Search table/category\"><select id=\"flowCategory\"></select></div>
                <p class=\"muted\" id=\"flowCount\"></p>
                <div class=\"table-wrap\"><table><thead><tr><th>Table</th><th>Category</th><th>Owner</th><th>Storage</th><th>Realtime</th><th>Upstream Hints</th></tr></thead><tbody id=\"flowRows\"></tbody></table></div>
            </div>
        </section>

        <section class=\"panel\" id=\"panel-metrics\">
            <div class=\"card\">
                <div class=\"toolbar\"><input id=\"metricSearch\" placeholder=\"Search table/metric\"></div>
                <p class=\"muted\" id=\"metricCount\"></p>
                <div class=\"table-wrap\"><table><thead><tr><th>Table</th><th>Metric</th><th>Formula Hint</th></tr></thead><tbody id=\"metricRows\"></tbody></table></div>
            </div>
        </section>

        <section class=\"panel\" id=\"panel-procedures\">
            <div class=\"card\">
                <div class=\"toolbar\"><input id=\"procedureSearch\" placeholder=\"Search procedure/type/owner\"></div>
                <p class=\"muted\" id=\"procedureCount\"></p>
                <div class=\"table-wrap\"><table><thead><tr><th>Procedure</th><th>Type</th><th>Return Type</th><th>Owner</th><th>Arguments</th></tr></thead><tbody id=\"procedureRows\"></tbody></table></div>
            </div>
        </section>

        <section class=\"panel\" id=\"panel-timers\">
            <div class=\"card\">
                <div class=\"toolbar\"><input id=\"timerSearch\" placeholder=\"Search timer/type/schedule\"></div>
                <p class=\"muted\" id=\"timerCount\"></p>
                <div class=\"table-wrap\"><table><thead><tr><th>Timer</th><th>Type</th><th>Priority</th><th>Schedule</th><th>Enabled</th><th>Next Run</th></tr></thead><tbody id=\"timerRows\"></tbody></table></div>
            </div>
        </section>
    </div>

    <script>
        const data = __DASHBOARD_DATA__;
        const tables = data.tables || [];
        const schemas = data.schemas || [];
        const relationships = data.relationships || [];
        const dataFlow = data.data_flow || [];
        const metrics = data.business_metrics || [];
        const externalMappings = data.external_mappings || { centers: [], replications: [] };
        const triggerFlows = data.trigger_flows || [];
        const procedureDetails = data.procedure_details || [];
        const timerDetails = data.timer_details || [];

        const fmt = (v) => {
            if (v === null || v === undefined) return "-";
            if (typeof v === "number") return v.toLocaleString();
            return String(v);
        };

        const formatTriggerOutput = (flow) => {
            const target = fmt(flow.output_table);
            if (String(flow.type || '').toUpperCase() !== 'RELAY') return target;
            const host = flow.relay_host ? String(flow.relay_host) : '-';
            const port = flow.relay_port ? String(flow.relay_port) : '-';
            return `${target} (${host}:${port})`;
        };

        document.getElementById("source").textContent =
            "URL: " + data.url + " | User: " + data.user + " | Driver: " + data.driver_class;
        document.getElementById("generated").textContent =
            "Generated (UTC): " + data.generated_at_utc;

        const kpiRows = tables.reduce((acc, t) => acc + (Number(t.row_estimate) || 0), 0);
        const kpiRealtime = tables.filter((t) => t.is_realtime === true).length;
        const kpiSchemaRows = schemas.reduce((acc, s) => acc + (s.columns ? s.columns.length : 0), 0);
        const kpiRel = relationships.length;
        const kpiMetrics = metrics.reduce((acc, m) => acc + (m.suggested_metrics || []).length, 0);
        const kpis = [
            ["Tables", tables.length],
            ["Estimated Rows", kpiRows.toLocaleString()],
            ["Schema Fields", kpiSchemaRows],
            ["Relations", kpiRel],
            ["Metric Hints", kpiMetrics],
        ];
        const kpiEl = document.getElementById("kpis");
        kpiEl.innerHTML = kpis.map(([label, value]) => '<div class="card"><div class="label">' + label + '</div><div class="value">' + value + '</div></div>').join("");

        const tabBtns = [...document.querySelectorAll(".tab-btn")];
        const panels = [...document.querySelectorAll(".panel")];
        tabBtns.forEach((btn) => {
            btn.addEventListener("click", () => {
                tabBtns.forEach((b) => b.classList.remove("active"));
                panels.forEach((p) => p.classList.remove("active"));
                btn.classList.add("active");
                const id = "panel-" + btn.dataset.tab;
                const panel = document.getElementById(id);
                if (panel) panel.classList.add("active");
            });
        });

        const countBy = (arr, key) => {
            const m = new Map();
            for (const item of arr) {
                const k = String(item[key] ?? "UNKNOWN");
                m.set(k, (m.get(k) || 0) + 1);
            }
            return [...m.entries()].sort((a, b) => b[1] - a[1]);
        };
        const renderBars = (targetId, items) => {
            const max = items.reduce((m, i) => Math.max(m, i[1]), 1);
            const target = document.getElementById(targetId);
            target.innerHTML = items.map(([name, val]) =>
                '<div class="bar-row"><div class="bar-name">' + name + '</div><div class="bar-wrap"><div class="bar" style="width:' + Math.max(4, (val/max)*100).toFixed(1) + '%"></div></div><div class="bar-num">' + val + '</div></div>'
            ).join("");
        };
        renderBars("ownerBars", countBy(tables, "owner"));
        renderBars("largestBars", [...tables].sort((a,b)=> (Number(b.row_estimate)||0)-(Number(a.row_estimate)||0)).slice(0,10).map((t)=>[t.name, Number(t.row_estimate)||0]));

        const tableSearch = document.getElementById("tableSearch");
        const ownerFilter = document.getElementById("ownerFilter");
        const policyFilter = document.getElementById("policyFilter");
        ownerFilter.innerHTML = ["ALL", ...new Set(tables.map((t)=>String(t.owner ?? "UNKNOWN")))].sort().map((o)=>'<option value="'+o+'">Owner: '+o+'</option>').join("");
        policyFilter.innerHTML = ["ALL", ...new Set(tables.map((t)=>String(t.change_policy ?? "UNKNOWN")))].sort().map((p)=>'<option value="'+p+'">Policy: '+p+'</option>').join("");

        const renderTables = () => {
            const s = tableSearch.value.trim().toLowerCase();
            const owner = ownerFilter.value;
            const policy = policyFilter.value;
            const filtered = tables.filter((t) => {
                const okS = !s || String(t.name).toLowerCase().includes(s);
                const okO = owner === "ALL" || String(t.owner ?? "UNKNOWN") === owner;
                const okP = policy === "ALL" || String(t.change_policy ?? "UNKNOWN") === policy;
                return okS && okO && okP;
            });
            document.getElementById("tableCount").textContent = "Showing " + filtered.length + " of " + tables.length + " tables";
            document.getElementById("tableRows").innerHTML = filtered.map((t) =>
                "<tr>" +
                "<td><strong>" + fmt(t.name) + "</strong></td>" +
                "<td><span class='pill'>" + fmt(t.owner) + "</span></td>" +
                "<td>" + fmt(t.change_policy) + "</td>" +
                "<td>" + fmt(t.scope) + "</td>" +
                "<td>" + fmt(t.row_estimate) + "</td>" +
                "<td>" + fmt(t.column_count) + "</td>" +
                "<td>" + (t.is_realtime === null ? "-" : (t.is_realtime ? "Yes" : "No")) + "</td>" +
                "</tr>"
            ).join("");
        };
        tableSearch.addEventListener("input", renderTables);
        ownerFilter.addEventListener("change", renderTables);
        policyFilter.addEventListener("change", renderTables);
        renderTables();

        const schemaSearch = document.getElementById("schemaSearch");
        const flattenedSchema = schemas.flatMap((s) => (s.columns || []).map((c) => ({ table: s.table, column: c.name, type: c.type, nullable: c.nullable, index_mode: c.index_mode })));
        const renderSchema = () => {
            const s = schemaSearch.value.trim().toLowerCase();
            const filtered = flattenedSchema.filter((r) => !s || String(r.table).toLowerCase().includes(s) || String(r.column).toLowerCase().includes(s));
            document.getElementById("schemaCount").textContent = "Showing " + filtered.length + " of " + flattenedSchema.length + " columns";
            document.getElementById("schemaRows").innerHTML = filtered.map((r) =>
                "<tr><td><strong>" + fmt(r.table) + "</strong></td><td>" + fmt(r.column) + "</td><td>" + fmt(r.type) + "</td><td>" + fmt(r.nullable) + "</td><td>" + fmt(r.index_mode) + "</td></tr>"
            ).join("");
        };
        schemaSearch.addEventListener("input", renderSchema);
        renderSchema();

        const relSearch = document.getElementById("relSearch");
        const renderRelationships = () => {
            const s = relSearch.value.trim().toLowerCase();
            const filtered = relationships.filter((r) => {
                const keys = (r.shared_keys || []).join(",").toLowerCase();
                return !s || String(r.left_table).toLowerCase().includes(s) || String(r.right_table).toLowerCase().includes(s) || keys.includes(s);
            });
            document.getElementById("relCount").textContent = "Showing " + filtered.length + " of " + relationships.length + " candidates";
            document.getElementById("relRows").innerHTML = filtered.map((r) =>
                "<tr><td><strong>" + fmt(r.left_table) + "</strong></td><td><strong>" + fmt(r.right_table) + "</strong></td><td>" + fmt((r.shared_keys || []).join(", ")) + "</td><td>" + fmt(r.strength) + "</td></tr>"
            ).join("");
        };
        relSearch.addEventListener("input", renderRelationships);
        renderRelationships();

        const flowSearch = document.getElementById("flowSearch");
        const flowCategory = document.getElementById("flowCategory");
        flowCategory.innerHTML = ["ALL", ...new Set(dataFlow.map((d)=>String(d.category||"unknown")))].sort().map((c)=>'<option value="'+c+'">Category: '+c+'</option>').join("");
        const renderFlow = () => {
            const s = flowSearch.value.trim().toLowerCase();
            const c = flowCategory.value;
            const filtered = dataFlow.filter((r) => {
                const okS = !s || String(r.table).toLowerCase().includes(s) || String(r.category).toLowerCase().includes(s);
                const okC = c === "ALL" || String(r.category) === c;
                return okS && okC;
            });
            document.getElementById("flowCount").textContent = "Showing " + filtered.length + " of " + dataFlow.length + " mappings";
            document.getElementById("flowRows").innerHTML = filtered.map((r) =>
                "<tr><td><strong>" + fmt(r.table) + "</strong></td><td>" + fmt(r.category) + "</td><td>" + fmt(r.owner) + "</td><td>" + fmt(r.storage_mode) + "</td><td>" + fmt(r.is_realtime) + "</td><td>" + fmt((r.upstream_hints || []).join(", ")) + "</td></tr>"
            ).join("");
        };
        flowSearch.addEventListener("input", renderFlow);
        flowCategory.addEventListener("change", renderFlow);
        renderFlow();

        const metricSearch = document.getElementById("metricSearch");
        const flattenedMetrics = metrics.flatMap((m) => (m.suggested_metrics || []).map((s) => ({ table: m.table, metric: s.metric, formula: s.formula_hint })));
        const renderMetrics = () => {
            const s = metricSearch.value.trim().toLowerCase();
            const filtered = flattenedMetrics.filter((r) => !s || String(r.table).toLowerCase().includes(s) || String(r.metric).toLowerCase().includes(s) || String(r.formula).toLowerCase().includes(s));
            document.getElementById("metricCount").textContent = "Showing " + filtered.length + " of " + flattenedMetrics.length + " metric hints";
            document.getElementById("metricRows").innerHTML = filtered.map((r) =>
                "<tr><td><strong>" + fmt(r.table) + "</strong></td><td>" + fmt(r.metric) + "</td><td>" + fmt(r.formula) + "</td></tr>"
            ).join("");
        };
        metricSearch.addEventListener("input", renderMetrics);
        renderMetrics();

        const procedureSearch = document.getElementById("procedureSearch");
        const renderProcedures = () => {
            const s = procedureSearch.value.trim().toLowerCase();
            const filtered = procedureDetails.filter((p) => {
                return !s ||
                    String(p.name).toLowerCase().includes(s) ||
                    String(p.procedure_type).toLowerCase().includes(s) ||
                    String(p.owner).toLowerCase().includes(s) ||
                    String(p.arguments).toLowerCase().includes(s);
            });
            document.getElementById("procedureCount").textContent = "Showing " + filtered.length + " of " + procedureDetails.length + " procedures";
            document.getElementById("procedureRows").innerHTML = filtered.map((p) =>
                "<tr><td><strong>" + fmt(p.name) + "</strong></td><td>" + fmt(p.procedure_type) + "</td><td>" + fmt(p.return_type) + "</td><td>" + fmt(p.owner) + "</td><td>" + fmt(p.arguments) + "</td></tr>"
            ).join("");
        };
        procedureSearch.addEventListener("input", renderProcedures);
        renderProcedures();

        const timerSearch = document.getElementById("timerSearch");
        const renderTimers = () => {
            const s = timerSearch.value.trim().toLowerCase();
            const filtered = timerDetails.filter((t) => {
                return !s ||
                    String(t.name).toLowerCase().includes(s) ||
                    String(t.timer_type).toLowerCase().includes(s) ||
                    String(t.schedule).toLowerCase().includes(s);
            });
            document.getElementById("timerCount").textContent = "Showing " + filtered.length + " of " + timerDetails.length + " timers";
            document.getElementById("timerRows").innerHTML = filtered.map((t) =>
                "<tr><td><strong>" + fmt(t.name) + "</strong></td><td>" + fmt(t.timer_type) + "</td><td>" + fmt(t.priority) + "</td><td>" + fmt(t.schedule) + "</td><td>" + fmt(t.enabled) + "</td><td>" + fmt(t.next_run_time) + "</td></tr>"
            ).join("");
        };
        timerSearch.addEventListener("input", renderTimers);
        renderTimers();

        const centers = externalMappings.centers || [];
        const replications = externalMappings.replications || [];
        document.getElementById("centerCount").textContent = "Total centers: " + centers.length;
        document.getElementById("replCount").textContent = "Total replications: " + replications.length;
        document.getElementById("centerRows").innerHTML = centers.map((r) =>
            "<tr>" +
            "<td><strong>" + fmt(r[0]) + "</strong></td>" +
            "<td>" + fmt(r[1]) + "</td>" +
            "<td>" + fmt(r[4]) + "</td>" +
            "<td>" + fmt(r[5]) + "</td>" +
            "<td>" + fmt(r[6]) + "</td>" +
            "</tr>"
        ).join("");
        document.getElementById("replRows").innerHTML = replications.map((r) =>
            "<tr>" +
            "<td><strong>" + fmt(r[0]) + "</strong></td>" +
            "<td>" + fmt(r[1]) + "</td>" +
            "<td>" + fmt(r[2]) + "</td>" +
            "<td>" + fmt(r[3]) + "</td>" +
            "<td>" + fmt(r[6]) + "</td>" +
            "<td>" + fmt(r[7]) + "</td>" +
            "</tr>"
        ).join("");
        document.getElementById("triggerCount").textContent = "Total trigger flows: " + triggerFlows.length;
        document.getElementById("triggerRows").innerHTML = triggerFlows.map((f) =>
            "<tr>" +
            "<td><strong>" + fmt(f.trigger) + "</strong></td>" +
            "<td>" + fmt(f.type) + "</td>" +
            "<td>" + fmt((f.input_tables || []).join(", ")) + "</td>" +
            "<td>" + formatTriggerOutput(f) + "</td>" +
            "<td>" + fmt(f.enabled) + "</td>" +
            "<td>" + fmt(f.priority) + "</td>" +
            "</tr>"
        ).join("");
                const outputLabel = String(formatTriggerOutput(f) || "(none)");

        const renderLineageGraph = (flows) => {
            const svg = document.getElementById("lineageGraph");
            const summary = document.getElementById("lineageSummary");
            if (!svg || !summary) return;

            const activeFlows = (flows || []).filter((f) => f && f.enabled !== false);
            if (activeFlows.length === 0) {
                summary.textContent = "No active trigger flow to visualize.";
                svg.setAttribute("viewBox", "0 0 760 180");
                svg.innerHTML = "<text x='24' y='80' class='lineage-label'>No trigger flow available</text>";
                return;
            }

            const producedTables = new Set(
                activeFlows
                    .map((f) => (f && f.output_table ? String(f.output_table) : ""))
                    .filter((v) => v.length > 0)
            );

            // Build trigger dependency graph: A -> B if A's output is an input of B.
            const outputProducer = new Map();
            activeFlows.forEach((f, i) => {
                const out = f && f.output_table ? String(f.output_table) : "";
                if (out && !outputProducer.has(out)) outputProducer.set(out, i);
            });

            const normalizeInputs = (f) =>
                Array.isArray(f.input_tables) ? f.input_tables.map((v) => String(v)) : [];

            const indegree = new Array(activeFlows.length).fill(0);
            const edges = new Map();
            for (let i = 0; i < activeFlows.length; i++) edges.set(i, []);

            activeFlows.forEach((f, idx) => {
                const inputs = normalizeInputs(f);
                for (const inp of inputs) {
                    const p = outputProducer.get(inp);
                    if (p !== undefined && p !== idx) {
                        edges.get(p).push(idx);
                        indegree[idx] += 1;
                    }
                }
            });

            const flowSortKey = (idx) => {
                const f = activeFlows[idx];
                const inputs = normalizeInputs(f);
                const externalInputs = inputs.filter((t) => !producedTables.has(t));
                const firstExternal = externalInputs.length ? externalInputs[0] : "";
                const pri = Number(f.priority ?? 0);
                const trig = String(f.trigger || "");
                return [firstExternal.toLowerCase(), pri, trig.toLowerCase()];
            };

            const compareIdx = (a, b) => {
                const ka = flowSortKey(a);
                const kb = flowSortKey(b);
                if (ka[0] !== kb[0]) return ka[0].localeCompare(kb[0]);
                if (ka[1] !== kb[1]) return ka[1] - kb[1];
                return ka[2].localeCompare(kb[2]);
            };

            // Kahn topological sort for generic source->target ordering.
            const ready = [];
            for (let i = 0; i < activeFlows.length; i++) {
                if (indegree[i] === 0) ready.push(i);
            }
            ready.sort(compareIdx);

            const orderedIndices = [];
            while (ready.length > 0) {
                const cur = ready.shift();
                orderedIndices.push(cur);
                const nexts = edges.get(cur) || [];
                for (const n of nexts) {
                    indegree[n] -= 1;
                    if (indegree[n] === 0) {
                        ready.push(n);
                        ready.sort(compareIdx);
                    }
                }
            }

            // If cycles/malformed deps exist, append remaining deterministically.
            for (let i = 0; i < activeFlows.length; i++) {
                if (!orderedIndices.includes(i)) orderedIndices.push(i);
            }

            const orderedFlows = orderedIndices.map((i) => activeFlows[i]);

            const maxRows = Math.max(orderedFlows.length, 1);
            const rowGap = 36;
            const topPad = 36;
            const height = Math.max(220, topPad * 2 + rowGap * maxRows);
            svg.setAttribute("viewBox", "0 0 760 " + height);

            const sx = 130;
            const tx = 380;
            const dx = 630;
            const rectW = 170;
            const rectH = 22;

            const esc = (v) => String(v)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/\"/g, "&quot;")
                .replace(/'/g, "&#39;");

            const edgeLines = [];
            const rowNodes = orderedFlows.map((f, i) => {
                const y = topPad + i * rowGap;
                const inputs = Array.isArray(f.input_tables) ? f.input_tables.map((v) => String(v)) : [];
                const sourceLabel = inputs.length > 0 ? inputs.join("\\n") : "(none)";
                const triggerLabel = String(f.trigger || "unknown_trigger");
                const outputLabel = String(f.output_table || "(none)");

                edgeLines.push(
                    "<path class='lineage-edge' d='M " + (sx + rectW / 2) + " " + y + " C " + (sx + 120) + " " + y + ", " + (tx - 120) + " " + y + ", " + (tx - rectW / 2) + " " + y + "'></path>"
                );
                edgeLines.push(
                    "<path class='lineage-edge' d='M " + (tx + rectW / 2) + " " + y + " C " + (tx + 120) + " " + y + ", " + (dx - 120) + " " + y + ", " + (dx - rectW / 2) + " " + y + "'></path>"
                );

                return {
                    sourceLabel,
                    triggerLabel,
                    outputLabel,
                    inputs,
                    y,
                };
            });


            const drawNode = (x, y, name, klass) => {
                const text = esc(name);
                const lines = String(name).split("\\n").map((s) => esc(s));
                const lineHeight = 11;
                const startY = y - ((lines.length - 1) * lineHeight) / 2;
                const tspans = lines.map((ln, i) =>
                    "<tspan class='lineage-label-tspan' x='" + x + "' y='" + (startY + i * lineHeight) + "'>" + ln + "</tspan>"
                ).join("");
                const dynamicHeight = Math.max(rectH, 12 + lines.length * lineHeight);
                return "<g><rect class='" + klass + "' x='" + (x - rectW / 2) + "' y='" + (y - dynamicHeight / 2) + "' width='" + rectW + "' height='" + dynamicHeight + "' rx='5'></rect><title>" + text + "</title><text class='lineage-label' x='" + x + "' y='" + y + "' text-anchor='middle'>" + tspans + "</text></g>";
            };

            const labels = [
                "<text class='lineage-label' x='" + sx + "' y='18' text-anchor='middle'>Source Tables (All Inputs)</text>",
                "<text class='lineage-label' x='" + tx + "' y='18' text-anchor='middle'>Triggers</text>",
                "<text class='lineage-label' x='" + dx + "' y='18' text-anchor='middle'>Target Tables</text>",
            ].join("");

            const sourceNodes = rowNodes.map((n) => {
                return drawNode(sx, n.y, n.sourceLabel, "lineage-node-table");
            }).join("");
            const triggerNodes = rowNodes.map((n) => {
                return drawNode(tx, n.y, n.triggerLabel, "lineage-node-trigger");
            }).join("");
            const targetNodes = rowNodes.map((n) => {
                return drawNode(dx, n.y, n.outputLabel, "lineage-node-table");
            }).join("");

            summary.textContent = "Ordered flows: " + rowNodes.length + " (auto dependency order: source -> trigger -> target)";
            svg.innerHTML = "<defs><marker id='arrow' markerWidth='9' markerHeight='6' refX='8' refY='3' orient='auto'><path d='M0,0 L9,3 L0,6 z' fill='#8f8a84'></path></marker></defs>" + labels + edgeLines.join("") + sourceNodes + triggerNodes + targetNodes;
        };

        renderLineageGraph(triggerFlows);
    </script>
</body>
</html>
"""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
                html.replace("__DASHBOARD_DATA__", dashboard_json),
                encoding="utf-8",
        )


def write_schema_markdown(path: Path, payload: dict[str, Any]) -> None:
    schemas = payload["schemas"]
    lines = [
        "# Schema Catalog",
        "",
        f"Generated at (UTC): {payload['generated_at_utc']}",
        "",
        f"Total tables with schema: {len(schemas)}",
        "",
    ]

    for schema in schemas:
        lines.append(f"## {schema['table']}")
        lines.append("")
        lines.append(f"- Columns: {schema['column_count']}")
        if schema.get("errors"):
            for err in schema["errors"]:
                lines.append(f"- Error: {err}")
        lines.append("")
        if schema.get("columns"):
            lines.append("| Column | Type | Nullable | Index Mode |")
            lines.append("|---|---|---|---|")
            for col in schema["columns"]:
                lines.append(
                    f"| {col['name']} | {col['type']} | {col['nullable']} | {col['index_mode']} |"
                )
            lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_relationships_markdown(path: Path, payload: dict[str, Any]) -> None:
    rels = payload["relationships"]
    lines = [
        "# Relationship Candidates",
        "",
        f"Generated at (UTC): {payload['generated_at_utc']}",
        "",
        f"Candidates found: {len(rels)}",
        "",
        "| Left Table | Right Table | Shared Keys | Strength |",
        "|---|---|---|---|",
    ]
    for rel in rels:
        keys = ", ".join(rel["shared_keys"])
        lines.append(
            f"| {rel['left_table']} | {rel['right_table']} | {keys} | {rel['strength']} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_dataflow_markdown(path: Path, payload: dict[str, Any]) -> None:
    flow = payload["data_flow"]
    trigger_flows = payload.get("trigger_flows", [])
    lines = [
        "# Data Flow Classification",
        "",
        f"Generated at (UTC): {payload['generated_at_utc']}",
        "",
        "| Table | Category | Owner | Storage Mode | Realtime | Upstream Hints |",
        "|---|---|---|---|---|---|",
    ]
    for row in flow:
        hints = ", ".join(row["upstream_hints"])
        lines.append(
            f"| {row['table']} | {row['category']} | {row['owner']} | {row['storage_mode']} | {row['is_realtime']} | {hints} |"
        )

    lines.extend([
        "",
        "## Trigger Flow (Input -> Output)",
        "",
        "| Trigger | Type | Inputs | Output | Enabled | Priority |",
        "|---|---|---|---|---|---|",
    ])
    for trg in trigger_flows:
        output_label = str(trg["output_table"])
        if str(trg.get("type") or "").upper() == "RELAY":
            relay_host = trg.get("relay_host") or "-"
            relay_port = trg.get("relay_port") or "-"
            output_label = f"{output_label} ({relay_host}:{relay_port})"
        lines.append(
            f"| {trg['trigger']} | {trg['type']} | {', '.join(trg['input_tables'])} | {output_label} | {trg['enabled']} | {trg['priority']} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_metrics_markdown(path: Path, payload: dict[str, Any]) -> None:
    metrics = payload["business_metrics"]
    lines = [
        "# Business Metric Candidates",
        "",
        f"Generated at (UTC): {payload['generated_at_utc']}",
        "",
    ]
    for entry in metrics:
        lines.append(f"## {entry['table']}")
        lines.append("")
        lines.append(f"- Numeric columns: {', '.join(entry['numeric_columns'])}")
        for metric in entry["suggested_metrics"]:
            lines.append(
                f"- {metric['metric']}: {metric['formula_hint']}"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_external_markdown(path: Path, payload: dict[str, Any]) -> None:
    external = payload.get("external_mappings", {})
    centers = external.get("centers", [])
    replications = external.get("replications", [])

    lines = [
        "# External Mappings",
        "",
        f"Generated at (UTC): {payload['generated_at_utc']}",
        "",
        "## Centers",
        "",
        f"- Count: {len(centers)}",
        "",
        "| Raw Row |",
        "|---|",
    ]
    for row in centers:
        lines.append(f"| `{json.dumps(row, ensure_ascii=True)}` |")

    lines.extend([
        "",
        "## Replications",
        "",
        f"- Count: {len(replications)}",
        "",
        "| Raw Row |",
        "|---|",
    ])
    for row in replications:
        lines.append(f"| `{json.dumps(row, ensure_ascii=True)}` |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_triggers_markdown(path: Path, payload: dict[str, Any]) -> None:
    trigger_details = payload.get("trigger_details", [])
    trigger_flows = payload.get("trigger_flows", [])

    lines = [
        "# Trigger Flow",
        "",
        f"Generated at (UTC): {payload['generated_at_utc']}",
        "",
        f"Trigger count: {len(trigger_details)}",
        "",
        "## Flow Map",
        "",
        "| Trigger | Type | Inputs | Output | Enabled |",
        "|---|---|---|---|---|",
    ]
    for flow in trigger_flows:
        output_label = str(flow["output_table"])
        if str(flow.get("type") or "").upper() == "RELAY":
            relay_host = flow.get("relay_host") or "-"
            relay_port = flow.get("relay_port") or "-"
            output_label = f"{output_label} ({relay_host}:{relay_port})"
        lines.append(
            f"| {flow['trigger']} | {flow['type']} | {', '.join(flow['input_tables'])} | {output_label} | {flow['enabled']} |"
        )

    lines.extend([
        "",
        "## Trigger Definitions",
        "",
    ])
    for trg in trigger_details:
        lines.append(f"### {trg['name']}")
        lines.append("")
        lines.append(f"- Type: {trg['type']}")
        lines.append(f"- Priority: {trg['priority']}")
        lines.append(f"- Owner: {trg['owner']}")
        if str(trg.get("type") or "").upper() == "RELAY":
            lines.append(f"- Relay host: {trg.get('relay_host') or '-'}")
            lines.append(f"- Relay port: {trg.get('relay_port') or '-'}")
        lines.append(f"- Enabled: {trg['enabled']}")
        lines.append(f"- Input tables: {', '.join(trg['input_tables'])}")
        lines.append(f"- Output table: {trg['output_table']}")
        if trg.get("ddl_error"):
            lines.append(f"- DDL error: {trg['ddl_error']}")
        lines.append("")
        if trg.get("ddl"):
            lines.append("```sql")
            lines.append(trg["ddl"].rstrip())
            lines.append("```")
            lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_procedures_markdown(path: Path, payload: dict[str, Any]) -> None:
    procedures = payload.get("procedure_details", [])
    lines = [
        "# Procedures",
        "",
        f"Generated at (UTC): {payload['generated_at_utc']}",
        "",
        f"Procedure count: {len(procedures)}",
        "",
        "| Procedure | Type | Return Type | Owner |",
        "|---|---|---|---|",
    ]
    for proc in procedures:
        lines.append(
            f"| {proc['name']} | {proc['procedure_type']} | {proc['return_type']} | {proc['owner']} |"
        )

    lines.extend([
        "",
        "## Procedure Definitions",
        "",
    ])
    for proc in procedures:
        lines.append(f"### {proc['name']}")
        lines.append("")
        lines.append(f"- Type: {proc['procedure_type']}")
        lines.append(f"- Return type: {proc['return_type']}")
        lines.append(f"- Arguments: {proc['arguments']}")
        lines.append(f"- Owner: {proc['owner']}")
        if proc.get("ddl_error"):
            lines.append(f"- DDL error: {proc['ddl_error']}")
        lines.append("")
        if proc.get("ddl"):
            lines.append("```sql")
            lines.append(proc["ddl"].rstrip())
            lines.append("```")
            lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_timers_markdown(path: Path, payload: dict[str, Any]) -> None:
    timers = payload.get("timer_details", [])
    lines = [
        "# Timers",
        "",
        f"Generated at (UTC): {payload['generated_at_utc']}",
        "",
        f"Timer count: {len(timers)}",
        "",
        "| Timer | Type | Priority | Schedule | Enabled |",
        "|---|---|---|---|---|",
    ]
    for timer in timers:
        lines.append(
            f"| {timer['name']} | {timer['timer_type']} | {timer['priority']} | {timer['schedule']} | {timer['enabled']} |"
        )

    lines.extend([
        "",
        "## Timer Definitions",
        "",
    ])
    for timer in timers:
        lines.append(f"### {timer['name']}")
        lines.append("")
        lines.append(f"- Type: {timer['timer_type']}")
        lines.append(f"- Priority: {timer['priority']}")
        lines.append(f"- Schedule: {timer['schedule']}")
        lines.append(f"- Owner: {timer['owner']}")
        lines.append(f"- Last run time: {timer['last_run_time']}")
        lines.append(f"- Next run time: {timer['next_run_time']}")
        lines.append(f"- Enabled: {timer['enabled']}")
        if timer.get("ddl_error"):
            lines.append(f"- DDL error: {timer['ddl_error']}")
        lines.append("")
        if timer.get("ddl"):
            lines.append("```sql")
            lines.append(timer["ddl"].rstrip())
            lines.append("```")
            lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_instances_config(path: Path) -> list[dict[str, Any]]:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
                instances = raw
        elif isinstance(raw, dict) and isinstance(raw.get("instances"), list):
                instances = raw["instances"]
        else:
                raise ValueError("instances config must be a list or an object with an 'instances' list")

        out: list[dict[str, Any]] = []
        for idx, item in enumerate(instances, start=1):
                if not isinstance(item, dict):
                        raise ValueError(f"instance entry #{idx} must be an object")
                out.append({**item, "_config_path": str(path)})
        return out


def write_instances_config(path: Path, instances: list[dict[str, Any]]) -> None:
        cleaned: list[dict[str, Any]] = []
        for item in instances:
                entry = {k: v for k, v in item.items() if not str(k).startswith("_")}
                cleaned.append(entry)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"instances": cleaned}, indent=2) + "\n", encoding="utf-8")


def _instances_key_path(config_path: Path) -> Path:
        return config_path.parent / ".instances.key"


def _load_instances_secret(config_path: Path) -> bytes:
        env_secret = os.getenv("AMI_INSTANCE_SECRET")
        if env_secret:
                return env_secret.encode("utf-8")

        key_path = _instances_key_path(config_path)
        if key_path.exists():
                return key_path.read_text(encoding="utf-8").strip().encode("utf-8")

        secret_text = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")
        key_path.write_text(secret_text + "\n", encoding="utf-8")
        try:
                os.chmod(key_path, 0o600)
        except OSError:
                pass
        return secret_text.encode("utf-8")


def _xor_bytes(left: bytes, right: bytes) -> bytes:
        return bytes(a ^ b for a, b in zip(left, right))


def _derive_stream(secret: bytes, salt: bytes, nonce: bytes, size: int) -> bytes:
        key = hashlib.pbkdf2_hmac("sha256", secret, salt, 120000, dklen=32)
        out = bytearray()
        counter = 0
        while len(out) < size:
                out.extend(hmac.new(key, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest())
                counter += 1
        return bytes(out[:size])


def encrypt_instance_password(password: str, config_path: Path) -> str:
        secret = _load_instances_secret(config_path)
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(16)
        plain = password.encode("utf-8")
        stream = _derive_stream(secret, salt, nonce, len(plain))
        cipher = _xor_bytes(plain, stream)
        mac_key = hashlib.pbkdf2_hmac("sha256", secret, salt + nonce, 120000, dklen=32)
        mac = hmac.new(mac_key, salt + nonce + cipher, hashlib.sha256).digest()
        packed = base64.urlsafe_b64encode(salt + nonce + cipher + mac).decode("ascii")
        return f"enc:v1:{packed}"


def decrypt_instance_password(ciphertext: str, config_path: Path) -> str:
        if not ciphertext.startswith("enc:v1:"):
                raise ValueError("Unsupported encrypted password format")
        raw = base64.urlsafe_b64decode(ciphertext.split(":", 2)[2].encode("ascii"))
        if len(raw) < 64:
                raise ValueError("Encrypted password payload is malformed")
        salt = raw[:16]
        nonce = raw[16:32]
        cipher = raw[32:-32]
        mac = raw[-32:]
        secret = _load_instances_secret(config_path)
        mac_key = hashlib.pbkdf2_hmac("sha256", secret, salt + nonce, 120000, dklen=32)
        expected_mac = hmac.new(mac_key, salt + nonce + cipher, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
                raise ValueError("Encrypted password verification failed")
        stream = _derive_stream(secret, salt, nonce, len(cipher))
        return _xor_bytes(cipher, stream).decode("utf-8")


def resolve_instance_password(instance_cfg: dict[str, Any], fallback: str | None) -> str:
        if instance_cfg.get("password"):
                return str(instance_cfg["password"])
        if instance_cfg.get("password_encrypted"):
            config_path_raw = instance_cfg.get("_config_path")
            if not config_path_raw:
                raise ValueError("Encrypted password is missing its config path context")
            return decrypt_instance_password(str(instance_cfg["password_encrypted"]), Path(str(config_path_raw)))
        if instance_cfg.get("password_env"):
                env_name = str(instance_cfg["password_env"])
                env_value = os.getenv(env_name)
                if env_value:
                        return env_value
        if fallback:
                return fallback
        raise ValueError(
                f"Missing password for instance '{instance_cfg.get('name', 'unknown')}'. "
                "Set password, password_env, or AMI_DB_PASSWORD."
        )


def collect_instance_snapshot(instance_cfg: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
        name = str(instance_cfg.get("name") or instance_cfg.get("id") or instance_cfg.get("url") or "instance")
        driver_class = str(instance_cfg.get("driver_class") or args.driver_class)
        adapter = str(instance_cfg.get("adapter") or args.adapter or "jdbc").lower()
        url = str(instance_cfg.get("url") or args.url)
        user = str(instance_cfg.get("user") or args.user)
        jar_path = str(instance_cfg.get("jar_path") or args.jar_path)
        java_home = str(instance_cfg.get("java_home") or args.java_home)
        telnet_host = instance_cfg.get("telnet_host") or args.telnet_host
        telnet_port = instance_cfg.get("telnet_port") or args.telnet_port
        telnet_login_command = str(
            instance_cfg.get("telnet_login_command") or args.telnet_login_command
        )
        telnet_prompt = str(instance_cfg.get("telnet_prompt") or args.telnet_prompt)
        telnet_timeout_sec = float(
            instance_cfg.get("telnet_timeout_sec") or args.telnet_timeout_sec
        )
        password = resolve_instance_password(instance_cfg, args.password)

        connection = None
        cursor = None
        rows: list[tuple[Any, ...]] = []
        schemas: list[dict[str, Any]] = []
        centers: list[tuple[Any, ...]] = []
        replications: list[tuple[Any, ...]] = []
        trigger_rows: list[tuple[Any, ...]] = []
        trigger_details: list[dict[str, Any]] = []
        procedure_rows: list[tuple[Any, ...]] = []
        procedure_details: list[dict[str, Any]] = []
        timer_rows: list[tuple[Any, ...]] = []
        timer_details: list[dict[str, Any]] = []

        try:
                connection = connect_db(
                    adapter=adapter,
                        driver_class=driver_class,
                        url=url,
                        user=user,
                        password=password,
                        jar_path=jar_path,
                        java_home=java_home,
                    telnet_host=str(telnet_host) if telnet_host else None,
                    telnet_port=int(telnet_port) if telnet_port else None,
                    telnet_login_command=telnet_login_command,
                    telnet_prompt=telnet_prompt,
                    telnet_timeout_sec=telnet_timeout_sec,
                )
                cursor = connection.cursor()
                rows = fetch_show_tables(cursor)
                centers = fetch_show_centers(cursor)
                replications = fetch_show_replications(cursor)
                trigger_rows = fetch_show_triggers(cursor)
                trigger_details = fetch_trigger_details(cursor, trigger_rows)
                procedure_rows = fetch_show_procedures(cursor)
                procedure_details = fetch_procedure_details(cursor, procedure_rows)
                timer_rows = fetch_show_timers(cursor)
                timer_details = fetch_timer_details(cursor, timer_rows)
                for row in rows:
                        table_name = str(row[0])
                        schemas.append(fetch_table_schema(cursor, table_name))
        finally:
                if cursor is not None:
                        cursor.close()
                if connection is not None:
                        connection.close()

        def normalize_value(value: Any) -> Any:
                if value is None or isinstance(value, (bool, int, float, str)):
                        return value
                return str(value)

        normalized_rows = [[normalize_value(v) for v in row] for row in rows]
        normalized_centers = [[normalize_value(v) for v in row] for row in centers]
        normalized_replications = [[normalize_value(v) for v in row] for row in replications]

        table_records = build_table_records(normalized_rows)
        relationships = infer_relationships(schemas)
        data_flow = classify_data_flow(table_records, schemas)
        business_metrics = infer_business_metrics(schemas)
        trigger_flows = derive_trigger_flows(trigger_details)

        return {
                "name": name,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "url": url,
                "user": user,
                "driver_class": driver_class,
                "row_count": len(rows),
                "tables": table_records,
                "schemas": schemas,
                "relationships": relationships,
                "data_flow": data_flow,
                "business_metrics": business_metrics,
                "external_mappings": {
                        "centers": normalized_centers,
                        "replications": normalized_replications,
                },
                "trigger_details": trigger_details,
                "trigger_flows": trigger_flows,
                "procedure_details": procedure_details,
                "timer_details": timer_details,
        }


def write_multi_instance_dashboard(path: Path, payload: dict[str, Any]) -> None:
        data_json = json.dumps(payload, ensure_ascii=True)
        html = """<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>AMI Flow Viewer</title>
    <style>
        :root { --bg:#f6f3ed; --card:#fff; --ink:#2b2926; --muted:#6a635b; --line:#e7dfd4; --brand:#0b728f; }
        * { box-sizing:border-box; }
        body { margin:0; font-family:Segoe UI,Tahoma,sans-serif; background:var(--bg); color:var(--ink); }
        .app { display:grid; grid-template-columns: 320px 1fr; min-height:100vh; }
        .left { border-right:1px solid var(--line); background:#fff; overflow:auto; }
        .right { overflow:auto; padding:16px; }
        .head { padding:14px; border-bottom:1px solid var(--line); position:sticky; top:0; background:#fff; z-index:2; }
        .head h1 { margin:0; font-size:20px; }
        .head p { margin:4px 0 0; color:var(--muted); font-size:12px; }
        .tree { padding:10px; }
        .tree details { border:1px solid var(--line); border-radius:10px; background:#faf8f5; margin-bottom:8px; }
        .tree summary { cursor:pointer; list-style:none; padding:8px 10px; font-weight:700; }
        .tree summary::-webkit-details-marker { display:none; }
        .leaf { display:block; width:100%; border:0; background:transparent; text-align:left; padding:7px 12px; cursor:pointer; color:var(--ink); }
        .leaf:hover { background:#eef7fa; }
        .leaf.active { background:var(--brand); color:#fff; }
        .panel { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px; }
        .panel h2 { margin:0 0 10px; }
        .meta { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:8px; margin-bottom:10px; }
        .k { border:1px solid var(--line); border-radius:10px; padding:8px; background:#fcfbf9; }
        .k .n { color:var(--muted); font-size:11px; text-transform:uppercase; }
        .k .v { margin-top:4px; font-weight:700; }
        .stack { display:grid; gap:12px; }
        .chart-card { border:1px solid var(--line); border-radius:10px; background:#fcfbf9; padding:10px; }
        .chart-card p { margin:0 0 8px; color:var(--muted); font-size:12px; }
        .svg-wrap { overflow:auto; border:1px solid #f2ece2; border-radius:10px; background:#fff; }
        .lineage-label { fill:#594f46; font-size:10px; font-family:Segoe UI,Tahoma,sans-serif; }
        .lineage-label-tspan { dominant-baseline:middle; }
        .lineage-edge { stroke:#8f8a84; stroke-width:1.4; fill:none; marker-end:url(#arrow); }
        .lineage-node-table { fill:#e8f3f6; stroke:#0b728f; stroke-width:1.1; }
        .lineage-node-trigger { fill:#fce8cc; stroke:#c77d1a; stroke-width:1.1; }
        table { width:100%; border-collapse:collapse; font-size:12px; }
        th,td { border-bottom:1px solid #f2ece2; text-align:left; padding:8px; vertical-align:top; }
        th { background:#f9f5ef; position:sticky; top:0; }
        .tbl { max-height:70vh; overflow:auto; border:1px solid var(--line); border-radius:10px; }
        @media (max-width: 980px) { .app { grid-template-columns:1fr; } .left { border-right:0; border-bottom:1px solid var(--line);} .meta{grid-template-columns:1fr 1fr;} }
    </style>
</head>
<body>
    <div class=\"app\">
        <aside class=\"left\">
            <div class=\"head\">
                <h1>AMI Flow Viewer</h1>
                <p id=\"globalMeta\"></p>
            </div>
            <div class=\"tree\" id=\"tree\"></div>
        </aside>
        <main class=\"right\">
            <section class=\"panel\">
                <h2 id=\"title\">Select a node</h2>
                <div class=\"meta\" id=\"meta\"></div>
                <div id=\"tableWrap\"></div>
            </section>
        </main>
    </div>
    <script>
        const payload = __AMI_DATA__;
        const instances = payload.instances || [];
        const tree = document.getElementById('tree');
        const title = document.getElementById('title');
        const meta = document.getElementById('meta');
        const tableWrap = document.getElementById('tableWrap');
        const globalMeta = document.getElementById('globalMeta');
        const params = new URLSearchParams(window.location.search);
        const targetInstance = (params.get('instance') || '').toLowerCase();
        globalMeta.textContent = `Instances: ${instances.length} | Generated: ${payload.generated_at_utc}`;

        const fmt = (v) => (v === null || v === undefined ? '-' : String(v));
        const viewDefs = [
            ['overview', 'Overview'],
            ['tables', 'Tables'],
            ['trigger_flows', 'Trigger Flow'],
            ['procedure_details', 'Procedures'],
            ['timer_details', 'Timers'],
            ['relationships', 'Relationships'],
            ['data_flow', 'Data Flow'],
            ['business_metrics', 'Metrics'],
        ];

        const renderRows = (headers, rows) => {
            const th = headers.map((h) => `<th>${h}</th>`).join('');
            const tr = rows.map((r) => `<tr>${r.map((c) => `<td>${fmt(c)}</td>`).join('')}</tr>`).join('');
            return `<div class="tbl"><table><thead><tr>${th}</tr></thead><tbody>${tr}</tbody></table></div>`;
        };

        const formatTriggerOutput = (flow) => {
            const target = fmt(flow.output_table);
            if (String(flow.type || '').toUpperCase() !== 'RELAY') return target;
            const host = flow.relay_host ? String(flow.relay_host) : '-';
            const port = flow.relay_port ? String(flow.relay_port) : '-';
            return `${target} (${host}:${port})`;
        };
                const outputLabel = String(formatTriggerOutput(f) || '(none)');

        const esc = (v) => String(v)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\"/g, '&quot;')
            .replace(/'/g, '&#39;');

        const renderLineageGraph = (svg, summary, flows) => {
            if (!svg || !summary) return;

            const activeFlows = (flows || []).filter((f) => f && f.enabled !== false);
            if (activeFlows.length === 0) {
                summary.textContent = 'No active trigger flow to visualize.';
                svg.setAttribute('viewBox', '0 0 760 180');
                svg.innerHTML = "<text x='24' y='80' class='lineage-label'>No trigger flow available</text>";
                return;
            }

            const producedTables = new Set(
                activeFlows
                    .map((f) => (f && f.output_table ? String(f.output_table) : ''))
                    .filter((v) => v.length > 0)
            );

            const outputProducer = new Map();
            activeFlows.forEach((f, i) => {
                const out = f && f.output_table ? String(f.output_table) : '';
                if (out && !outputProducer.has(out)) outputProducer.set(out, i);
            });

            const normalizeInputs = (f) =>
                Array.isArray(f.input_tables) ? f.input_tables.map((v) => String(v)) : [];

            const indegree = new Array(activeFlows.length).fill(0);
            const edges = new Map();
            for (let i = 0; i < activeFlows.length; i++) edges.set(i, []);

            activeFlows.forEach((f, idx) => {
                const inputs = normalizeInputs(f);
                for (const inp of inputs) {
                    const producerIdx = outputProducer.get(inp);
                    if (producerIdx !== undefined && producerIdx !== idx) {
                        edges.get(producerIdx).push(idx);
                        indegree[idx] += 1;
                    }
                }
            });

            const flowSortKey = (idx) => {
                const f = activeFlows[idx];
                const inputs = normalizeInputs(f);
                const externalInputs = inputs.filter((t) => !producedTables.has(t));
                const firstExternal = externalInputs.length ? externalInputs[0] : '';
                const pri = Number(f.priority ?? 0);
                const trig = String(f.trigger || '');
                return [firstExternal.toLowerCase(), pri, trig.toLowerCase()];
            };

            const compareIdx = (a, b) => {
                const ka = flowSortKey(a);
                const kb = flowSortKey(b);
                if (ka[0] !== kb[0]) return ka[0].localeCompare(kb[0]);
                if (ka[1] !== kb[1]) return ka[1] - kb[1];
                return ka[2].localeCompare(kb[2]);
            };

            const ready = [];
            for (let i = 0; i < activeFlows.length; i++) {
                if (indegree[i] === 0) ready.push(i);
            }
            ready.sort(compareIdx);

            const orderedIndices = [];
            while (ready.length > 0) {
                const cur = ready.shift();
                orderedIndices.push(cur);
                const nexts = edges.get(cur) || [];
                for (const nextIdx of nexts) {
                    indegree[nextIdx] -= 1;
                    if (indegree[nextIdx] === 0) {
                        ready.push(nextIdx);
                        ready.sort(compareIdx);
                    }
                }
            }

            for (let i = 0; i < activeFlows.length; i++) {
                if (!orderedIndices.includes(i)) orderedIndices.push(i);
            }

            const orderedFlows = orderedIndices.map((i) => activeFlows[i]);
            const maxRows = Math.max(orderedFlows.length, 1);
            const rowGap = 36;
            const topPad = 36;
            const height = Math.max(220, topPad * 2 + rowGap * maxRows);
            svg.setAttribute('viewBox', `0 0 760 ${height}`);

            const sx = 130;
            const tx = 380;
            const dx = 630;
            const rectW = 170;
            const rectH = 22;

            const edgeLines = [];
            const rowNodes = orderedFlows.map((f, i) => {
                const y = topPad + i * rowGap;
                const inputs = Array.isArray(f.input_tables) ? f.input_tables.map((v) => String(v)) : [];
                const sourceLabel = inputs.length > 0 ? inputs.join('\\n') : '(none)';
                const triggerLabel = String(f.trigger || 'unknown_trigger');
                const outputLabel = String(f.output_table || '(none)');

                edgeLines.push(
                    `<path class='lineage-edge' d='M ${sx + rectW / 2} ${y} C ${sx + 120} ${y}, ${tx - 120} ${y}, ${tx - rectW / 2} ${y}'></path>`
                );
                edgeLines.push(
                    `<path class='lineage-edge' d='M ${tx + rectW / 2} ${y} C ${tx + 120} ${y}, ${dx - 120} ${y}, ${dx - rectW / 2} ${y}'></path>`
                );

                return { sourceLabel, triggerLabel, outputLabel, y };
            });

            const drawNode = (x, y, name, klass) => {
                const text = esc(name);
                const lines = String(name).split('\\n').map((s) => esc(s));
                const lineHeight = 11;
                const startY = y - ((lines.length - 1) * lineHeight) / 2;
                const tspans = lines.map((ln, i) =>
                    `<tspan class='lineage-label-tspan' x='${x}' y='${startY + i * lineHeight}'>${ln}</tspan>`
                ).join('');
                const dynamicHeight = Math.max(rectH, 12 + lines.length * lineHeight);
                return `<g><rect class='${klass}' x='${x - rectW / 2}' y='${y - dynamicHeight / 2}' width='${rectW}' height='${dynamicHeight}' rx='5'></rect><title>${text}</title><text class='lineage-label' x='${x}' y='${y}' text-anchor='middle'>${tspans}</text></g>`;
            };

            const labels = [
                `<text class='lineage-label' x='${sx}' y='18' text-anchor='middle'>Source Tables (All Inputs)</text>`,
                `<text class='lineage-label' x='${tx}' y='18' text-anchor='middle'>Triggers</text>`,
                `<text class='lineage-label' x='${dx}' y='18' text-anchor='middle'>Target Tables</text>`,
            ].join('');

            const sourceNodes = rowNodes.map((n) => drawNode(sx, n.y, n.sourceLabel, 'lineage-node-table')).join('');
            const triggerNodes = rowNodes.map((n) => drawNode(tx, n.y, n.triggerLabel, 'lineage-node-trigger')).join('');
            const targetNodes = rowNodes.map((n) => drawNode(dx, n.y, n.outputLabel, 'lineage-node-table')).join('');

            summary.textContent = `Ordered flows: ${rowNodes.length} (auto dependency order: source -> trigger -> target)`;
            svg.innerHTML = "<defs><marker id='arrow' markerWidth='9' markerHeight='6' refX='8' refY='3' orient='auto'><path d='M0,0 L9,3 L0,6 z' fill='#8f8a84'></path></marker></defs>" + labels + edgeLines.join('') + sourceNodes + triggerNodes + targetNodes;
        };

        const renderView = (inst, view) => {
            title.textContent = `${inst.name} / ${view}`;
            const kpis = [
                ['URL', inst.url],
                ['User', inst.user],
                ['Tables', (inst.tables || []).length],
                ['Triggers', (inst.trigger_flows || []).length],
                ['Procedures', (inst.procedure_details || []).length],
                ['Timers', (inst.timer_details || []).length],
            ];
            meta.innerHTML = kpis.map(([n,v]) => `<div class=\"k\"><div class=\"n\">${n}</div><div class=\"v\">${fmt(v)}</div></div>`).join('');

            if (view === 'overview') {
                tableWrap.innerHTML = renderRows(
                    ['Section', 'Count'],
                    [
                        ['Tables', (inst.tables || []).length],
                        ['Schemas', (inst.schemas || []).length],
                        ['Relationships', (inst.relationships || []).length],
                        ['Trigger Flows', (inst.trigger_flows || []).length],
                        ['Procedures', (inst.procedure_details || []).length],
                        ['Timers', (inst.timer_details || []).length],
                    ]
                );
                return;
            }

            if (view === 'tables') {
                tableWrap.innerHTML = renderRows(
                    ['Table', 'Owner', 'Rows', 'Columns', 'Realtime'],
                    (inst.tables || []).map((t) => [t.name, t.owner, t.row_estimate, t.column_count, t.is_realtime])
                );
                return;
            }

            if (view === 'trigger_flows') {
                tableWrap.innerHTML = `<div class="stack"><div class="chart-card"><p id="lineageSummary"></p><div class="svg-wrap"><svg id="lineageGraph" width="100%" height="520" role="img" aria-label="Trigger flow chart"></svg></div></div>${renderRows(
                    ['Trigger', 'Type', 'Inputs', 'Output', 'Enabled', 'Priority'],
                    (inst.trigger_flows || []).map((t) => [t.trigger, t.type, (t.input_tables || []).join(', '), formatTriggerOutput(t), t.enabled, t.priority])
                )}</div>`;
                renderLineageGraph(
                    document.getElementById('lineageGraph'),
                    document.getElementById('lineageSummary'),
                    inst.trigger_flows || []
                );
                return;
            }

            if (view === 'procedure_details') {
                tableWrap.innerHTML = renderRows(
                    ['Procedure', 'Type', 'Return', 'Owner', 'Arguments'],
                    (inst.procedure_details || []).map((p) => [p.name, p.procedure_type, p.return_type, p.owner, p.arguments])
                );
                return;
            }

            if (view === 'timer_details') {
                tableWrap.innerHTML = renderRows(
                    ['Timer', 'Type', 'Priority', 'Schedule', 'Enabled', 'Next Run'],
                    (inst.timer_details || []).map((t) => [t.name, t.timer_type, t.priority, t.schedule, t.enabled, t.next_run_time])
                );
                return;
            }

            if (view === 'relationships') {
                tableWrap.innerHTML = renderRows(
                    ['Left', 'Right', 'Shared Keys', 'Strength'],
                    (inst.relationships || []).map((r) => [r.left_table, r.right_table, (r.shared_keys || []).join(', '), r.strength])
                );
                return;
            }

            if (view === 'data_flow') {
                tableWrap.innerHTML = renderRows(
                    ['Table', 'Category', 'Owner', 'Realtime', 'Hints'],
                    (inst.data_flow || []).map((d) => [d.table, d.category, d.owner, d.is_realtime, (d.upstream_hints || []).join(', ')])
                );
                return;
            }

            if (view === 'business_metrics') {
                tableWrap.innerHTML = renderRows(
                    ['Table', 'Metric', 'Formula Hint'],
                    (inst.business_metrics || []).flatMap((m) => (m.suggested_metrics || []).map((s) => [m.table, s.metric, s.formula_hint]))
                );
            }
        };

        let firstAction = null;
        instances.forEach((inst, idx) => {
            const details = document.createElement('details');
            const isTarget = targetInstance && String(inst.name || '').toLowerCase() === targetInstance;
            details.open = isTarget || (!targetInstance && idx === 0);
            const summary = document.createElement('summary');
            summary.textContent = inst.name;
            details.appendChild(summary);

            viewDefs.forEach(([key, label], jdx) => {
                const btn = document.createElement('button');
                btn.className = 'leaf';
                btn.textContent = label;
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.leaf.active').forEach((e) => e.classList.remove('active'));
                    btn.classList.add('active');
                    renderView(inst, key);
                });
                details.appendChild(btn);
                if (isTarget && jdx === 0) {
                    firstAction = () => btn.click();
                } else if (!firstAction && idx === 0 && jdx === 0) {
                    firstAction = () => btn.click();
                }
            });

            tree.appendChild(details);
        });
        if (firstAction) firstAction();
    </script>
</body>
</html>
"""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html.replace("__AMI_DATA__", data_json), encoding="utf-8")


def main() -> int:
    args = parse_args()

    if args.instances_config:
        config_path = Path(args.instances_config)
        if not config_path.exists():
            print(f"Instances config not found: {config_path}", file=sys.stderr)
            return 2

        try:
            instance_cfgs = load_instances_config(config_path)
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to parse instances config: {exc}", file=sys.stderr)
            return 2

        if not instance_cfgs:
            print("Instances config is empty.", file=sys.stderr)
            return 2

        max_instances = max(1, int(args.max_instances))
        selected_cfgs = instance_cfgs[:max_instances]
        if len(instance_cfgs) > max_instances:
            print(f"Limiting instances to first {max_instances} entries from config.")

        instances: list[dict[str, Any]] = []
        failures = 0
        for cfg in selected_cfgs:
            try:
                instances.append(collect_instance_snapshot(cfg, args))
            except Exception as exc:  # noqa: BLE001
                failures += 1
                name = str(cfg.get("name") or cfg.get("id") or cfg.get("url") or "instance")
                instances.append(
                    {
                        "name": name,
                        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                        "url": str(cfg.get("url") or ""),
                        "user": str(cfg.get("user") or ""),
                        "driver_class": str(cfg.get("driver_class") or args.driver_class),
                        "error": str(exc),
                        "tables": [],
                        "schemas": [],
                        "relationships": [],
                        "data_flow": [],
                        "business_metrics": [],
                        "external_mappings": {"centers": [], "replications": []},
                        "trigger_details": [],
                        "trigger_flows": [],
                        "procedure_details": [],
                        "timer_details": [],
                    }
                )

        multi_payload = {
            "project_name": "AMI Flow Viewer",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "instance_count": len(instances),
            "instances": instances,
        }

        output_multi_json = Path(args.output_multi_json)
        output_multi_dashboard = Path(args.output_multi_dashboard)
        write_json(output_multi_json, multi_payload)
        write_multi_instance_dashboard(output_multi_dashboard, multi_payload)
        print(f"Wrote AMI Flow Viewer JSON to {output_multi_json}")
        print(f"Wrote AMI Flow Viewer dashboard to {output_multi_dashboard}")
        if failures:
            print(f"Completed with {failures} instance failures.")
        return 0

    if not args.password:
        print(
            "Missing password. Pass --password or set AMI_DB_PASSWORD.",
            file=sys.stderr,
        )
        return 2

    connection = None
    cursor = None
    rows: list[tuple[Any, ...]] = []
    schemas: list[dict[str, Any]] = []
    centers: list[tuple[Any, ...]] = []
    replications: list[tuple[Any, ...]] = []
    trigger_rows: list[tuple[Any, ...]] = []
    trigger_details: list[dict[str, Any]] = []
    procedure_rows: list[tuple[Any, ...]] = []
    procedure_details: list[dict[str, Any]] = []
    timer_rows: list[tuple[Any, ...]] = []
    timer_details: list[dict[str, Any]] = []
    try:
        connection = connect_db(
            adapter=args.adapter,
            driver_class=args.driver_class,
            url=args.url,
            user=args.user,
            password=args.password,
            jar_path=args.jar_path,
            java_home=args.java_home,
            telnet_host=args.telnet_host,
            telnet_port=args.telnet_port,
            telnet_login_command=args.telnet_login_command,
            telnet_prompt=args.telnet_prompt,
            telnet_timeout_sec=args.telnet_timeout_sec,
        )
        cursor = connection.cursor()
        rows = fetch_show_tables(cursor)
        centers = fetch_show_centers(cursor)
        replications = fetch_show_replications(cursor)
        trigger_rows = fetch_show_triggers(cursor)
        trigger_details = fetch_trigger_details(cursor, trigger_rows)
        procedure_rows = fetch_show_procedures(cursor)
        procedure_details = fetch_procedure_details(cursor, procedure_rows)
        timer_rows = fetch_show_timers(cursor)
        timer_details = fetch_timer_details(cursor, timer_rows)
        for row in rows:
            table_name = str(row[0])
            schemas.append(fetch_table_schema(cursor, table_name))
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    def normalize_value(value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        return str(value)

    normalized_rows = [
        [normalize_value(value) for value in row]
        for row in rows
    ]
    normalized_centers = [
        [normalize_value(value) for value in row]
        for row in centers
    ]
    normalized_replications = [
        [normalize_value(value) for value in row]
        for row in replications
    ]

    trigger_flows = derive_trigger_flows(trigger_details)

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "query": "show tables",
        "url": args.url,
        "user": args.user,
        "driver_class": args.driver_class,
        "row_count": len(rows),
        "rows": normalized_rows,
    }

    table_records = build_table_records(normalized_rows)
    relationships = infer_relationships(schemas)
    data_flow = classify_data_flow(table_records, schemas)
    business_metrics = infer_business_metrics(schemas)

    logic_payload = {
        "generated_at_utc": payload["generated_at_utc"],
        "url": args.url,
        "user": args.user,
        "driver_class": args.driver_class,
        "schemas": schemas,
        "relationships": relationships,
        "data_flow": data_flow,
        "business_metrics": business_metrics,
        "external_mappings": {
            "centers": normalized_centers,
            "replications": normalized_replications,
        },
        "trigger_details": trigger_details,
        "trigger_flows": trigger_flows,
        "procedure_details": procedure_details,
        "timer_details": timer_details,
    }

    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_dashboard = Path(args.output_dashboard)
    output_schema_md = Path(args.output_schema_md)
    output_schema_json = Path(args.output_schema_json)
    output_relationships_md = Path(args.output_relationships_md)
    output_relationships_json = Path(args.output_relationships_json)
    output_dataflow_md = Path(args.output_dataflow_md)
    output_dataflow_json = Path(args.output_dataflow_json)
    output_metrics_md = Path(args.output_metrics_md)
    output_metrics_json = Path(args.output_metrics_json)
    output_external_md = Path(args.output_external_md)
    output_external_json = Path(args.output_external_json)
    output_triggers_md = Path(args.output_triggers_md)
    output_triggers_json = Path(args.output_triggers_json)
    output_procedures_md = Path(args.output_procedures_md)
    output_procedures_json = Path(args.output_procedures_json)
    output_timers_md = Path(args.output_timers_md)
    output_timers_json = Path(args.output_timers_json)

    write_markdown(output_md, payload)
    write_json(output_json, payload)
    write_dashboard(output_dashboard, payload, logic_payload)
    write_schema_markdown(output_schema_md, logic_payload)
    write_relationships_markdown(output_relationships_md, logic_payload)
    write_dataflow_markdown(output_dataflow_md, logic_payload)
    write_metrics_markdown(output_metrics_md, logic_payload)
    write_external_markdown(output_external_md, logic_payload)
    write_triggers_markdown(output_triggers_md, logic_payload)
    write_procedures_markdown(output_procedures_md, logic_payload)
    write_timers_markdown(output_timers_md, logic_payload)
    write_json(output_schema_json, {"schemas": schemas, "generated_at_utc": payload["generated_at_utc"]})
    write_json(
        output_relationships_json,
        {"relationships": relationships, "generated_at_utc": payload["generated_at_utc"]},
    )
    write_json(
        output_dataflow_json,
        {"data_flow": data_flow, "generated_at_utc": payload["generated_at_utc"]},
    )
    write_json(
        output_metrics_json,
        {"business_metrics": business_metrics, "generated_at_utc": payload["generated_at_utc"]},
    )
    write_json(
        output_external_json,
        {
            "external_mappings": {
                "centers": normalized_centers,
                "replications": normalized_replications,
            },
            "generated_at_utc": payload["generated_at_utc"],
        },
    )
    write_json(
        output_triggers_json,
        {
            "trigger_details": trigger_details,
            "trigger_flows": trigger_flows,
            "generated_at_utc": payload["generated_at_utc"],
        },
    )
    write_json(
        output_procedures_json,
        {
            "procedure_details": procedure_details,
            "generated_at_utc": payload["generated_at_utc"],
        },
    )
    write_json(
        output_timers_json,
        {
            "timer_details": timer_details,
            "generated_at_utc": payload["generated_at_utc"],
        },
    )

    print(f"Wrote {len(rows)} tables to {output_md}")
    print(f"Wrote JSON payload to {output_json}")
    print(f"Wrote dashboard to {output_dashboard}")
    print(f"Wrote schema catalog to {output_schema_md} and {output_schema_json}")
    print(
        f"Wrote relationship candidates to {output_relationships_md} and {output_relationships_json}"
    )
    print(f"Wrote data flow classification to {output_dataflow_md} and {output_dataflow_json}")
    print(f"Wrote business metrics to {output_metrics_md} and {output_metrics_json}")
    print(f"Wrote external mappings to {output_external_md} and {output_external_json}")
    print(f"Wrote trigger flow to {output_triggers_md} and {output_triggers_json}")
    print(f"Wrote procedures to {output_procedures_md} and {output_procedures_json}")
    print(f"Wrote timers to {output_timers_md} and {output_timers_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
