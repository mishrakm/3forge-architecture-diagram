#!/usr/bin/env python3
"""Serve AMI Flow Viewer static files plus live on-demand AMI API endpoints."""

from __future__ import annotations

import argparse
import http.server
import json
import os
import socket
import time
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
    fetch_show_procedures,
    fetch_show_replications,
    fetch_show_tables,
    fetch_show_timers,
    fetch_show_triggers,
    fetch_table_schema,
    fetch_timer_details,
    fetch_trigger_details,
    infer_business_metrics,
    infer_relationships,
    load_instances_config,
    resolve_instance_password,
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
}

ALLOWED_DESCRIBE_TYPES = {"table", "trigger", "procedure", "timer"}


@dataclass
class AppContext:
    docs_dir: Path
    instance_map: dict[str, dict[str, Any]]
    generator_args: argparse.Namespace


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
        "--java-home",
        default=os.getenv(
            "JAVA_HOME", "/usr/lib/jvm/java-17-openjdk-17.0.18.0.8-2.el9.x86_64"
        ),
        help="JAVA_HOME used to boot the JVM.",
    )
    return parser.parse_args()


def normalize_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def normalize_rows(rows: list[tuple[Any, ...]]) -> list[list[Any]]:
    return [[normalize_scalar(v) for v in row] for row in rows]


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


def query_section(instance_cfg: dict[str, Any], args: argparse.Namespace, section: str) -> dict[str, Any]:
    if section not in ALLOWED_VIEWS:
        raise ValueError(f"Unsupported section: {section}")

    driver_class = str(instance_cfg.get("driver_class") or args.driver_class)
    url = str(instance_cfg.get("url") or args.url)
    user = str(instance_cfg.get("user") or args.user)
    jar_path = str(instance_cfg.get("jar_path") or args.jar_path)
    java_home = str(instance_cfg.get("java_home") or args.java_home)
    password = resolve_instance_password(instance_cfg, args.password)

    started = time.time()
    connection = None
    cursor = None
    try:
        connection = connect_db(
            driver_class=driver_class,
            url=url,
            user=user,
            password=password,
            jar_path=jar_path,
            java_home=java_home,
        )
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
        else:
            payload = section_external_mappings(cursor)

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
        driver_class=str(instance_cfg.get("driver_class") or args.driver_class),
        url=str(instance_cfg.get("url") or args.url),
        user=str(instance_cfg.get("user") or args.user),
        password=resolve_instance_password(instance_cfg, args.password),
        jar_path=str(instance_cfg.get("jar_path") or args.jar_path),
        java_home=str(instance_cfg.get("java_home") or args.java_home),
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

    driver_class = str(instance_cfg.get("driver_class") or args.driver_class)
    url = str(instance_cfg.get("url") or args.url)
    user = str(instance_cfg.get("user") or args.user)
    jar_path = str(instance_cfg.get("jar_path") or args.jar_path)
    java_home = str(instance_cfg.get("java_home") or args.java_home)
    password = resolve_instance_password(instance_cfg, args.password)

    started = time.time()
    connection = None
    cursor = None
    try:
        connection = connect_db(
            driver_class=driver_class,
            url=url,
            user=user,
            password=password,
            jar_path=jar_path,
            java_home=java_home,
        )
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


class LiveRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Serve static files and live JSON endpoints."""

    app: AppContext

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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

    def handle_api_post(self, path: str) -> None:
        try:
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
            self.write_json(404, {"error": "Unknown API endpoint"})
        except Exception as exc:  # noqa: BLE001
            self.write_json(500, {"error": str(exc)})

    def handle_api(self, path: str) -> None:
        try:
            if path == "/api/health":
                self.write_json(200, {"status": "ok"})
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
        raw = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
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
        driver_class=args.driver_class,
        url=args.url,
        user=args.user,
        password=args.password,
        jar_path=args.jar_path,
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
        instance_map=instance_map,
        generator_args=generator_args,
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
