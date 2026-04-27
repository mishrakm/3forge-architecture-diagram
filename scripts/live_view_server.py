#!/usr/bin/env python3
"""Serve AMI Flow Viewer static files plus live on-demand AMI API endpoints."""

from __future__ import annotations

import argparse
import http.server
import json
import os
import re
import socket
import threading
import time
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from document_tables import (
    DEFAULTS,
    build_table_records,
    classify_data_flow,
    collect_instance_snapshot,
    connect_db,
    derive_trigger_flows,
    fetch_procedure_details,
    fetch_show_centers,
    fetch_show_datasources,
    fetch_show_procedures,
    fetch_show_replications,
    fetch_show_tables,
    fetch_show_timers,
    fetch_show_triggers,
    fetch_table_schema,
    fetch_timer_details,
    fetch_trigger_details,
    encrypt_instance_password,
    infer_business_metrics,
    infer_relationships,
    load_instances_config,
    resolve_instance_password,
    write_instances_config,
)

ALLOWED_VIEWS = {
    "overview",
    "tables",
    "trigger_flows",
    "procedure_details",
    "timer_details",
    "relationships",
    "data_flow",
    "business_metrics",
    "external_mappings",
    "datasources",
}

ALLOWED_DESCRIBE_TYPES = {"table", "trigger", "procedure", "method", "timer"}


@dataclass
class AppContext:
    docs_dir: Path
    instances_path: Path
    instance_map: dict[str, dict[str, Any]]
    generator_args: argparse.Namespace
    lock: threading.Lock


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve docs plus live AMI API for dynamic AMI Flow Viewer."
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=8080, help="Bind port (default: 8080).")
    parser.add_argument("--dir", default="docs", help="Directory to serve static files from.")
    parser.add_argument(
        "--instances-config",
        default=DEFAULTS["instances_config"],
        help="Path to instances.json used by live API endpoints.",
    )
    parser.add_argument(
        "--adapter",
        choices=["jdbc", "telnet"],
        default=os.getenv("AMI_DB_ADAPTER", DEFAULTS.get("adapter", "jdbc")),
        help="Default adapter for instances that omit adapter (jdbc|telnet).",
    )
    parser.add_argument(
        "--driver-class",
        default=os.getenv("AMI_DB_DRIVER", DEFAULTS["driver_class"]),
        help="Default JDBC driver for instances that omit driver_class.",
    )
    parser.add_argument(
        "--url",
        default=os.getenv("AMI_DB_URL", DEFAULTS["url"]),
        help="Fallback JDBC URL for instances that omit url.",
    )
    parser.add_argument(
        "--user",
        default=os.getenv("AMI_DB_USER", DEFAULTS["user"]),
        help="Fallback AMI DB user for instances that omit user.",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("AMI_DB_PASSWORD"),
        help="Fallback AMI DB password when instance config lacks password/password_env.",
    )
    parser.add_argument(
        "--jar-path",
        default=os.getenv("AMI_DB_JAR", DEFAULTS["jar_path"]),
        help="Fallback JDBC jar for instances that omit jar_path.",
    )
    parser.add_argument(
        "--telnet-host",
        default=os.getenv("AMI_TELNET_HOST"),
        help="Fallback telnet host for instances that omit telnet_host.",
    )
    parser.add_argument(
        "--telnet-port",
        type=int,
        default=int(os.getenv("AMI_TELNET_PORT", "0")) or None,
        help="Fallback telnet port for instances that omit telnet_port. If omitted, x280 -> x290 is applied.",
    )
    parser.add_argument(
        "--telnet-login-command",
        default=os.getenv("AMI_TELNET_LOGIN_COMMAND", "Login"),
        help="Username command for telnet sessions, e.g. 'Login'.",
    )
    parser.add_argument(
        "--telnet-prompt",
        default=os.getenv("AMI_TELNET_PROMPT", ">"),
        help="Prompt marker used to detect command completion in telnet mode.",
    )
    parser.add_argument(
        "--telnet-timeout-sec",
        type=float,
        default=float(os.getenv("AMI_TELNET_TIMEOUT_SEC", str(DEFAULTS.get("telnet_timeout_sec", 6.0)))),
        help="Telnet read timeout in seconds (fail-fast for missing prompt/login).",
    )
    parser.add_argument(
        "--java-home",
        default=os.getenv(
            "JAVA_HOME", "/usr/lib/jvm/java-17-openjdk-17.0.18.0.8-2.el9.x86_64"
        ),
        help="JAVA_HOME used to boot the JVM.",
    )
    return parser.parse_args()


def normalize_scalar(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return value
    if value is None or isinstance(value, (bool, int, str)):
        return value
    return str(value)


def normalize_rows(rows: list[tuple[Any, ...]]) -> list[list[Any]]:
    return [[normalize_scalar(v) for v in row] for row in rows]


def sanitize_for_json(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(k): sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(v) for v in value]
    if isinstance(value, tuple):
        return [sanitize_for_json(v) for v in value]
    return value


def section_overview(cursor: Any) -> dict[str, Any]:
    tables = fetch_show_tables(cursor)
    triggers = fetch_show_triggers(cursor)
    procedures = fetch_show_procedures(cursor)
    timers = fetch_show_timers(cursor)
    centers = fetch_show_centers(cursor)
    replications = fetch_show_replications(cursor)
    return {
        "counts": {
            "tables": len(tables),
            "triggers": len(triggers),
            "procedures": len(procedures),
            "timers": len(timers),
            "centers": len(centers),
            "replications": len(replications),
        }
    }


def section_tables(cursor: Any) -> dict[str, Any]:
    rows = fetch_show_tables(cursor)
    tables = build_table_records(normalize_rows(rows))
    return {"rows": tables}


def section_trigger_flows(cursor: Any) -> dict[str, Any]:
    trigger_rows = fetch_show_triggers(cursor)
    trigger_details = fetch_trigger_details(cursor, trigger_rows)
    return {
        "rows": derive_trigger_flows(trigger_details),
        "trigger_details": trigger_details,
    }


def section_procedures(cursor: Any) -> dict[str, Any]:
    procedure_rows = fetch_show_procedures(cursor)
    procedure_details = fetch_procedure_details(cursor, procedure_rows)
    return {"rows": procedure_details}


def section_timers(cursor: Any) -> dict[str, Any]:
    timer_rows = fetch_show_timers(cursor)
    timer_details = fetch_timer_details(cursor, timer_rows)
    return {"rows": timer_details}


def section_relationships(cursor: Any) -> dict[str, Any]:
    rows = fetch_show_tables(cursor)
    schemas = [fetch_table_schema(cursor, str(r[0])) for r in rows]
    rels = infer_relationships(schemas)
    return {"rows": rels}


def section_data_flow(cursor: Any) -> dict[str, Any]:
    rows = fetch_show_tables(cursor)
    normalized_rows = normalize_rows(rows)
    tables = build_table_records(normalized_rows)
    schemas = [fetch_table_schema(cursor, str(r[0])) for r in rows]
    flow = classify_data_flow(tables, schemas)
    return {"rows": flow}


def section_business_metrics(cursor: Any) -> dict[str, Any]:
    rows = fetch_show_tables(cursor)
    schemas = [fetch_table_schema(cursor, str(r[0])) for r in rows]
    metrics = infer_business_metrics(schemas)
    flat = [
        {
            "table": metric.get("table"),
            "metric": hint.get("metric"),
            "formula_hint": hint.get("formula_hint"),
        }
        for metric in metrics
        for hint in metric.get("suggested_metrics", [])
    ]
    return {"rows": flat}


def section_external_mappings(cursor: Any) -> dict[str, Any]:
    centers = normalize_rows(fetch_show_centers(cursor))
    replications = normalize_rows(fetch_show_replications(cursor))
    return {
        "centers": centers,
        "replications": replications,
    }


def section_datasources(cursor: Any) -> dict[str, Any]:
    rows = normalize_rows(fetch_show_datasources(cursor))
    return {"rows": rows}


def query_section(instance_cfg: dict[str, Any], args: argparse.Namespace, section: str) -> dict[str, Any]:
    if section not in ALLOWED_VIEWS:
        raise ValueError(f"Unsupported section: {section}")

    url = str(instance_cfg.get("url") or args.url)
    user = str(instance_cfg.get("user") or args.user)

    started = time.time()
    connection = None
    cursor = None
    try:
        connection = _make_connection(instance_cfg, args)
        cursor = connection.cursor()

        if section == "overview":
            payload = section_overview(cursor)
        elif section == "tables":
            payload = section_tables(cursor)
        elif section == "trigger_flows":
            payload = section_trigger_flows(cursor)
        elif section == "procedure_details":
            payload = section_procedures(cursor)
        elif section == "timer_details":
            payload = section_timers(cursor)
        elif section == "relationships":
            payload = section_relationships(cursor)
        elif section == "data_flow":
            payload = section_data_flow(cursor)
        elif section == "business_metrics":
            payload = section_business_metrics(cursor)
        elif section == "external_mappings":
            payload = section_external_mappings(cursor)
        else:
            payload = section_datasources(cursor)

        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "instance": str(instance_cfg.get("name") or instance_cfg.get("url") or "instance"),
            "section": section,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_ms": elapsed_ms,
            "url": url,
            "user": user,
            "payload": payload,
        }
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


_SAFE_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_.]*$')


def _validate_obj_name(name: str) -> None:
    if not _SAFE_NAME_RE.match(name) or any(c in name for c in (';', '\n', '\r', '"', "'")):
        raise ValueError(f"Invalid object name: {name!r}")


def _make_connection(instance_cfg: dict[str, Any], args: argparse.Namespace):  # type: ignore[return]
    return connect_db(
        adapter=str(instance_cfg.get("adapter") or args.adapter or "jdbc").lower(),
        driver_class=str(instance_cfg.get("driver_class") or args.driver_class),
        url=str(instance_cfg.get("url") or args.url),
        user=str(instance_cfg.get("user") or args.user),
        password=resolve_instance_password(instance_cfg, args.password),
        jar_path=str(instance_cfg.get("jar_path") or args.jar_path),
        java_home=str(instance_cfg.get("java_home") or args.java_home),
        telnet_host=(str(instance_cfg.get("telnet_host")) if instance_cfg.get("telnet_host") else args.telnet_host),
        telnet_port=(int(instance_cfg.get("telnet_port")) if instance_cfg.get("telnet_port") else args.telnet_port),
        telnet_login_command=str(instance_cfg.get("telnet_login_command") or args.telnet_login_command),
        telnet_prompt=str(instance_cfg.get("telnet_prompt") or args.telnet_prompt),
        telnet_timeout_sec=float(instance_cfg.get("telnet_timeout_sec") or args.telnet_timeout_sec),
    )


def query_table_data(
    instance_cfg: dict[str, Any],
    args: argparse.Namespace,
    table_name: str,
) -> dict[str, Any]:
    _validate_obj_name(table_name)
    started = time.time()
    connection = None
    cursor = None
    try:
        connection = _make_connection(instance_cfg, args)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
        col_names = [str(d[0]) for d in (cursor.description or [])]
        rows = normalize_rows(cursor.fetchall())
        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "instance": str(instance_cfg.get("name") or instance_cfg.get("url")),
            "table": table_name,
            "columns": col_names,
            "rows": rows,
            "row_count": len(rows),
            "elapsed_ms": elapsed_ms,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def query_execute(
    instance_cfg: dict[str, Any],
    args: argparse.Namespace,
    sql: str,
) -> dict[str, Any]:
    query = (sql or "").strip()
    if not query:
        raise ValueError("Query is empty")

    # Keep this to one statement per request.
    if ";" in query[:-1]:
        raise ValueError("Only a single SQL statement is allowed per execution")
    if query.endswith(";"):
        query = query[:-1].strip()

    started = time.time()
    connection = None
    cursor = None
    try:
        connection = _make_connection(instance_cfg, args)
        cursor = connection.cursor()
        cursor.execute(query)
        elapsed_ms = int((time.time() - started) * 1000)

        has_result_set = bool(getattr(cursor, "description", None))
        if has_result_set:
            columns = [str(d[0]) for d in (cursor.description or [])]
            rows = normalize_rows(cursor.fetchall())
            max_rows = 2000
            clipped = len(rows) > max_rows
            rows = rows[:max_rows]
            return {
                "instance": str(instance_cfg.get("name") or instance_cfg.get("url")),
                "sql": query,
                "elapsed_ms": elapsed_ms,
                "has_result_set": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "rows_clipped": clipped,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            }

        rowcount = getattr(cursor, "rowcount", None)
        return {
            "instance": str(instance_cfg.get("name") or instance_cfg.get("url")),
            "sql": query,
            "elapsed_ms": elapsed_ms,
            "has_result_set": False,
            "affected_rows": int(rowcount) if isinstance(rowcount, int) else rowcount,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def _safe_filename(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    slug = slug.strip("._")
    return slug or "instance"


def _md_row(cells: list[Any]) -> str:
    return "| " + " | ".join(str(c).replace("\n", " ") for c in cells) + " |"


def _build_database_design_markdown(snapshot: dict[str, Any]) -> str:
    lines: list[str] = []
    name = str(snapshot.get("name") or "instance")
    lines.append(f"# Database Design - {name}")
    lines.append("")
    lines.append(f"Generated (UTC): {snapshot.get('generated_at_utc', '-')}")
    lines.append(f"JDBC URL: {snapshot.get('url', '-')}")
    lines.append(f"User: {snapshot.get('user', '-')}")
    lines.append("")

    tables = snapshot.get("tables", []) or []
    schemas = snapshot.get("schemas", []) or []
    relationships = snapshot.get("relationships", []) or []
    data_flow = snapshot.get("data_flow", []) or []
    business_metrics = snapshot.get("business_metrics", []) or []
    external = snapshot.get("external_mappings", {}) or {}
    centers = external.get("centers", []) or []
    replications = external.get("replications", []) or []
    trigger_details = snapshot.get("trigger_details", []) or []
    trigger_flows = snapshot.get("trigger_flows", []) or []
    procedures = snapshot.get("procedure_details", []) or []
    timers = snapshot.get("timer_details", []) or []

    lines.append("## Overview")
    lines.append("")
    lines.append(_md_row(["Section", "Count"]))
    lines.append(_md_row(["---", "---"]))
    lines.append(_md_row(["Tables", len(tables)]))
    lines.append(_md_row(["Schemas", len(schemas)]))
    lines.append(_md_row(["Relationships", len(relationships)]))
    lines.append(_md_row(["Data Flow Hints", len(data_flow)]))
    lines.append(_md_row(["Business Metrics", len(business_metrics)]))
    lines.append(_md_row(["Centers", len(centers)]))
    lines.append(_md_row(["Replications", len(replications)]))
    lines.append(_md_row(["Trigger Details", len(trigger_details)]))
    lines.append(_md_row(["Trigger Flows", len(trigger_flows)]))
    lines.append(_md_row(["Procedures", len(procedures)]))
    lines.append(_md_row(["Timers", len(timers)]))
    lines.append("")

    lines.append("## Tables")
    lines.append("")
    lines.append(_md_row(["Table", "Owner", "Rows", "Columns", "Realtime"]))
    lines.append(_md_row(["---", "---", "---", "---", "---"]))
    for t in tables:
        lines.append(_md_row([
            t.get("name", "-"),
            t.get("owner", "-"),
            t.get("row_estimate", "-"),
            t.get("column_count", "-"),
            t.get("is_realtime", "-"),
        ]))
    lines.append("")

    lines.append("## Schema Catalog")
    lines.append("")
    for schema in schemas:
        table_name = schema.get("table", "-")
        lines.append(f"### {table_name}")
        lines.append("")
        lines.append(_md_row(["Column", "Type", "Nullable", "Index Mode"]))
        lines.append(_md_row(["---", "---", "---", "---"]))
        for col in (schema.get("columns", []) or []):
            lines.append(_md_row([
                col.get("name", "-"),
                col.get("type", "-"),
                col.get("nullable", "-"),
                col.get("index_mode", "-"),
            ]))
        lines.append("")

    lines.append("## Relationships")
    lines.append("")
    lines.append(_md_row(["Left Table", "Right Table", "Shared Keys", "Strength"]))
    lines.append(_md_row(["---", "---", "---", "---"]))
    for rel in relationships:
        lines.append(_md_row([
            rel.get("left_table", "-"),
            rel.get("right_table", "-"),
            ", ".join(rel.get("shared_keys", []) or []),
            rel.get("strength", "-"),
        ]))
    lines.append("")

    lines.append("## Data Flow")
    lines.append("")
    lines.append(_md_row(["Table", "Category", "Owner", "Realtime", "Upstream Hints"]))
    lines.append(_md_row(["---", "---", "---", "---", "---"]))
    for flow in data_flow:
        lines.append(_md_row([
            flow.get("table", "-"),
            flow.get("category", "-"),
            flow.get("owner", "-"),
            flow.get("is_realtime", "-"),
            ", ".join(flow.get("upstream_hints", []) or []),
        ]))
    lines.append("")

    lines.append("## Business Metrics")
    lines.append("")
    lines.append(_md_row(["Table", "Metric", "Formula Hint"]))
    lines.append(_md_row(["---", "---", "---"]))
    for metric in business_metrics:
        for hint in (metric.get("suggested_metrics", []) or []):
            lines.append(_md_row([
                metric.get("table", "-"),
                hint.get("metric", "-"),
                hint.get("formula_hint", "-"),
            ]))
    lines.append("")

    lines.append("## Replications")
    lines.append("")
    lines.append("### Centers")
    lines.append("")
    lines.append(_md_row(["Center", "Type", "Host", "Port", "Active", "Connected", "Connect Time"]))
    lines.append(_md_row(["---", "---", "---", "---", "---", "---", "---"]))
    for c in centers:
        row = list(c) + ["-"] * 7
        lines.append(_md_row([row[0], row[1], row[2], row[3], row[4], row[5], row[6]]))
    lines.append("")

    lines.append("### Replications")
    lines.append("")
    lines.append(_md_row(["Replication", "Center", "Table", "Type", "State", "Errors", "Direction", "Enabled"]))
    lines.append(_md_row(["---", "---", "---", "---", "---", "---", "---", "---"]))
    for r in replications:
        row = list(r) + ["-"] * 8
        lines.append(_md_row([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]]))
    lines.append("")

    lines.append("## Trigger Flow")
    lines.append("")
    lines.append(_md_row(["Trigger", "Type", "Inputs", "Output", "Enabled", "Priority"]))
    lines.append(_md_row(["---", "---", "---", "---", "---", "---"]))
    for trg in trigger_flows:
        lines.append(_md_row([
            trg.get("trigger", "-"),
            trg.get("type", "-"),
            ", ".join(trg.get("input_tables", []) or []),
            trg.get("output_table", "-"),
            trg.get("enabled", "-"),
            trg.get("priority", "-"),
        ]))
    lines.append("")

    lines.append("## Procedures")
    lines.append("")
    lines.append(_md_row(["Name", "Type", "Return Type", "Owner", "Arguments"]))
    lines.append(_md_row(["---", "---", "---", "---", "---"]))
    for p in procedures:
        lines.append(_md_row([
            p.get("name", "-"),
            p.get("procedure_type", "-"),
            p.get("return_type", "-"),
            p.get("owner", "-"),
            p.get("arguments", "-"),
        ]))
    lines.append("")

    lines.append("## Timers")
    lines.append("")
    lines.append(_md_row(["Name", "Type", "Priority", "Schedule", "Enabled", "Next Run"]))
    lines.append(_md_row(["---", "---", "---", "---", "---", "---"]))
    for t in timers:
        lines.append(_md_row([
            t.get("name", "-"),
            t.get("timer_type", "-"),
            t.get("priority", "-"),
            t.get("schedule", "-"),
            t.get("enabled", "-"),
            t.get("next_run_time", "-"),
        ]))
    lines.append("")

    return "\n".join(lines) + "\n"


def query_database_design_markdown(
    instance_cfg: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[str, str]:
    snapshot = collect_instance_snapshot(instance_cfg, args)
    instance_name = str(snapshot.get("name") or instance_cfg.get("name") or "instance")
    filename = f"database_design_{_safe_filename(instance_name)}.md"
    return filename, _build_database_design_markdown(snapshot)


def query_drop(
    instance_cfg: dict[str, Any],
    args: argparse.Namespace,
    obj_type: str,
    obj_name: str,
) -> dict[str, Any]:
    if obj_type not in ALLOWED_DESCRIBE_TYPES:
        raise ValueError(f"Unsupported drop type: {obj_type!r}")
    _validate_obj_name(obj_name)
    started = time.time()
    connection = None
    cursor = None
    try:
        connection = _make_connection(instance_cfg, args)
        cursor = connection.cursor()
        cursor.execute(f"DROP {obj_type} {obj_name}")
        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "instance": str(instance_cfg.get("name") or instance_cfg.get("url")),
            "object_type": obj_type,
            "object_name": obj_name,
            "dropped": True,
            "elapsed_ms": elapsed_ms,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def query_describe(
    instance_cfg: dict[str, Any],
    args: argparse.Namespace,
    obj_type: str,
    obj_name: str,
) -> dict[str, Any]:
    if obj_type not in ALLOWED_DESCRIBE_TYPES:
        raise ValueError(f"Unsupported describe type: {obj_type!r}")

    url = str(instance_cfg.get("url") or args.url)

    started = time.time()
    connection = None
    cursor = None
    try:
        connection = _make_connection(instance_cfg, args)
        cursor = connection.cursor()
        cursor.execute(f"describe {obj_type} {obj_name}")
        rows = cursor.fetchall()
        ddl = str(rows[0][0]) if rows else None
        elapsed_ms = int((time.time() - started) * 1000)
        return {
            "instance": str(instance_cfg.get("name") or url),
            "object_type": obj_type,
            "object_name": obj_name,
            "ddl": ddl,
            "elapsed_ms": elapsed_ms,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


INSTANCE_EDITABLE_FIELDS = {
    "name",
    "app_code",
    "mode",
    "center_id",
    "port",
    "url",
    "user",
    "jar_path",
    "adapter",
    "driver_class",
    "telnet_host",
    "telnet_port",
    "telnet_login_command",
    "telnet_prompt",
    "java_home",
}


def _public_instance_config(cfg: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in cfg.items() if not str(k).startswith("_") and k not in {"password", "password_encrypted", "password_env"}}
    out["has_password"] = bool(cfg.get("password") or cfg.get("password_encrypted") or cfg.get("password_env"))
    out["password_storage"] = (
        "encrypted" if cfg.get("password_encrypted") else
        "env" if cfg.get("password_env") else
        "plain" if cfg.get("password") else
        "none"
    )
    return out


def _reload_instances(app: AppContext) -> list[dict[str, Any]]:
    instances = load_instances_config(app.instances_path)
    app.instance_map = build_instance_map(instances)
    return instances


def _sanitize_instance_payload(payload: dict[str, Any], existing: dict[str, Any] | None, config_path: Path) -> dict[str, Any]:
    name = str(payload.get("name") or (existing or {}).get("name") or "").strip()
    if not name:
        raise ValueError("Instance name is required")

    entry: dict[str, Any] = {}
    for field in INSTANCE_EDITABLE_FIELDS:
        candidate = payload[field] if field in payload else (existing or {}).get(field)
        if candidate in (None, ""):
            continue
        if field in {"port", "telnet_port"}:
            entry[field] = int(candidate)
        else:
            entry[field] = str(candidate) if isinstance(candidate, Path) else candidate

    entry["name"] = name

    password = payload.get("password")
    if isinstance(password, str) and password.strip():
        entry["password_encrypted"] = encrypt_instance_password(password.strip(), config_path)
    elif existing and existing.get("password_encrypted"):
        entry["password_encrypted"] = existing["password_encrypted"]
    elif existing and existing.get("password_env"):
        entry["password_env"] = existing["password_env"]
    elif existing and existing.get("password"):
        entry["password"] = existing["password"]

    return entry


def _save_instance_config(app: AppContext, payload: dict[str, Any]) -> dict[str, Any]:
    with app.lock:
        instances = load_instances_config(app.instances_path)
        by_name = {str(item.get("name") or "").strip().lower(): item for item in instances}
        existing = by_name.get(str(payload.get("name") or "").strip().lower())
        entry = _sanitize_instance_payload(payload, existing, app.instances_path)

        updated = []
        replaced = False
        for item in instances:
            item_name = str(item.get("name") or "").strip().lower()
            if item_name == entry["name"].strip().lower():
                updated.append(entry)
                replaced = True
            else:
                updated.append(item)
        if not replaced:
            updated.append(entry)

        write_instances_config(app.instances_path, updated)
        _reload_instances(app)
        return _public_instance_config(build_instance_map([entry])[entry["name"].strip().lower()])


def _delete_instance_config(app: AppContext, instance_name: str) -> None:
    target = instance_name.strip().lower()
    if not target:
        raise ValueError("Instance name is required")
    with app.lock:
        instances = load_instances_config(app.instances_path)
        remaining = [item for item in instances if str(item.get("name") or "").strip().lower() != target]
        if len(remaining) == len(instances):
            raise ValueError(f"Unknown instance: {instance_name}")
        write_instances_config(app.instances_path, remaining)
        _reload_instances(app)


class LiveRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Serve static files and live JSON endpoints."""

    app: AppContext

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api(parsed.path)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api_post(parsed.path)
            return
        self.send_response(405)
        self.end_headers()

    def do_DELETE(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api_delete(parsed.path)
            return
        self.send_response(405)
        self.end_headers()

    def _read_json_body(self) -> dict[str, Any]:
        length_header = self.headers.get("Content-Length") or "0"
        try:
            length = int(length_header)
        except ValueError as exc:  # noqa: BLE001
            raise ValueError("Invalid Content-Length") from exc
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise ValueError("Invalid JSON payload") from exc

    def handle_api_post(self, path: str) -> None:
        try:
            if path == "/api/instances/config":
                payload = self._read_json_body()
                result = _save_instance_config(self.app, payload)
                self.write_json(200, {"saved": True, "instance": result})
                return

            prefix = "/api/instance/"
            if path.startswith(prefix):
                rest = path[len(prefix):]
                parts = [unquote(p) for p in rest.split("/") if p]
                if len(parts) == 4 and parts[1] == "drop":
                    instance_name, _, obj_type, obj_name = parts
                    cfg = self.app.instance_map.get(instance_name.lower())
                    if cfg is None:
                        self.write_json(404, {"error": f"Unknown instance: {instance_name}"})
                        return
                    result = query_drop(cfg, self.app.generator_args, obj_type, obj_name)
                    self.write_json(200, result)
                    return

                if len(parts) == 2 and parts[1] == "query":
                    instance_name, _ = parts
                    cfg = self.app.instance_map.get(instance_name.lower())
                    if cfg is None:
                        self.write_json(404, {"error": f"Unknown instance: {instance_name}"})
                        return
                    payload = self._read_json_body()
                    sql = str(payload.get("sql") or "")
                    result = query_execute(cfg, self.app.generator_args, sql)
                    self.write_json(200, result)
                    return
            self.write_json(404, {"error": "Unknown API endpoint"})
        except Exception as exc:  # noqa: BLE001
            self.write_json(500, {"error": str(exc)})

    def handle_api_delete(self, path: str) -> None:
        try:
            prefix = "/api/instances/config/"
            if path.startswith(prefix):
                instance_name = unquote(path[len(prefix):]).strip()
                _delete_instance_config(self.app, instance_name)
                self.write_json(200, {"deleted": True, "name": instance_name})
                return
            self.write_json(404, {"error": "Unknown API endpoint"})
        except Exception as exc:  # noqa: BLE001
            self.write_json(500, {"error": str(exc)})

    def handle_api(self, path: str) -> None:
        try:
            if path == "/api/health":
                self.write_json(200, {"status": "ok"})
                return

            if path == "/api/instances/config":
                rows = [_public_instance_config(cfg) for _, cfg in sorted(self.app.instance_map.items())]
                self.write_json(200, {"instances": rows})
                return

            if path == "/api/instances":
                rows = [
                    {
                        "name": cfg.get("name") or cfg.get("url") or key,
                        "url": cfg.get("url"),
                        "user": cfg.get("user") or self.app.generator_args.user,
                    }
                    for key, cfg in sorted(self.app.instance_map.items())
                ]
                self.write_json(200, {"instances": rows})
                return

            prefix = "/api/instance/"
            if path.startswith(prefix):
                rest = path[len(prefix) :]
                parts = [unquote(p) for p in rest.split("/") if p]

                # /api/instance/<name>/describe/<type>/<object>
                if len(parts) == 4 and parts[1] == "describe":
                    instance_name, _, obj_type, obj_name = parts
                    cfg = self.app.instance_map.get(instance_name.lower())
                    if cfg is None:
                        self.write_json(404, {"error": f"Unknown instance: {instance_name}"})
                        return
                    result = query_describe(cfg, self.app.generator_args, obj_type, obj_name)
                    self.write_json(200, result)
                    return

                # /api/instance/<name>/table_data/<tablename>
                if len(parts) == 3 and parts[1] == "table_data":
                    instance_name, _, table_name = parts
                    cfg = self.app.instance_map.get(instance_name.lower())
                    if cfg is None:
                        self.write_json(404, {"error": f"Unknown instance: {instance_name}"})
                        return
                    result = query_table_data(cfg, self.app.generator_args, table_name)
                    self.write_json(200, result)
                    return

                # /api/instance/<name>/database_design
                if len(parts) == 2 and parts[1] == "database_design":
                    instance_name, _ = parts
                    cfg = self.app.instance_map.get(instance_name.lower())
                    if cfg is None:
                        self.write_json(404, {"error": f"Unknown instance: {instance_name}"})
                        return
                    filename, markdown = query_database_design_markdown(cfg, self.app.generator_args)
                    self.write_text(200, markdown, "text/markdown; charset=utf-8", filename=filename)
                    return

                if len(parts) != 2:
                    self.write_json(400, {"error": "Expected /api/instance/<name>/<section>"})
                    return
                instance_name, section = parts
                cfg = self.app.instance_map.get(instance_name.lower())
                if cfg is None:
                    self.write_json(404, {"error": f"Unknown instance: {instance_name}"})
                    return
                result = query_section(cfg, self.app.generator_args, section)
                self.write_json(200, result)
                return

            self.write_json(404, {"error": "Unknown API endpoint"})
        except Exception as exc:  # noqa: BLE001
            self.write_json(500, {"error": str(exc)})

    def write_json(self, code: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(sanitize_for_json(payload), ensure_ascii=True, allow_nan=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def write_text(self, code: int, text: str, content_type: str, filename: str | None = None) -> None:
        raw = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def build_instance_map(instances: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for cfg in instances:
        name = str(cfg.get("name") or cfg.get("url") or "instance").strip()
        if not name:
            continue
        out[name.lower()] = {**cfg, "name": name}
    return out


def main() -> int:
    args = parse_args()
    docs_dir = Path(args.dir).resolve()
    if not docs_dir.exists() or not docs_dir.is_dir():
        raise SystemExit(f"Directory not found: {docs_dir}")

    instances_path = Path(args.instances_config).resolve()
    if not instances_path.exists():
        raise SystemExit(f"Instances config not found: {instances_path}")

    instances = load_instances_config(instances_path)
    if not instances:
        raise SystemExit("Instances config is empty.")

    generator_args = argparse.Namespace(
        adapter=args.adapter,
        driver_class=args.driver_class,
        url=args.url,
        user=args.user,
        password=args.password,
        jar_path=args.jar_path,
        telnet_host=args.telnet_host,
        telnet_port=args.telnet_port,
        telnet_login_command=args.telnet_login_command,
        telnet_prompt=args.telnet_prompt,
        telnet_timeout_sec=args.telnet_timeout_sec,
        java_home=args.java_home,
    )
    instance_map = build_instance_map(instances)

    handler = lambda *h_args, **h_kwargs: LiveRequestHandler(  # noqa: E731
        *h_args,
        directory=str(docs_dir),
        **h_kwargs,
    )
    LiveRequestHandler.app = AppContext(
        docs_dir=docs_dir,
        instances_path=instances_path,
        instance_map=instance_map,
        generator_args=generator_args,
        lock=threading.Lock(),
    )

    with http.server.ThreadingHTTPServer((args.host, args.port), handler) as httpd:
        print(f"Serving static docs from: {docs_dir}")
        print(f"Live API endpoint:      http://{args.host}:{args.port}/api/instances")
        if args.host == "0.0.0.0":
            print(f"Portal URL:             http://127.0.0.1:{args.port}/index.html")
            try:
                host_ips = sorted(set(socket.gethostbyname_ex(socket.gethostname())[2]))
                for ip in host_ips:
                    if ip and not ip.startswith("127."):
                        print(f"LAN URL:                http://{ip}:{args.port}/index.html")
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
