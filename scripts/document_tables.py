#!/usr/bin/env python3
"""Generate first-pass documentation for AMI DB tables using JDBC."""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jaydebeapi
import jpype


DEFAULTS = {
    "driver_class": "com.f1.ami.amidb.jdbc.AmiDbJdbcDriver",
    "url": "jdbc:amisql:125.125.126.5:3280",
    "user": "pwadmin",
    "jar_path": "./out.jar",
    "output_md": "./docs/tables.md",
    "output_json": "./docs/tables.json",
    "output_dashboard": "./docs/tables_dashboard.html",
    "output_schema_md": "./docs/schema_catalog.md",
    "output_schema_json": "./docs/schema_catalog.json",
    "output_relationships_md": "./docs/relationships.md",
    "output_relationships_json": "./docs/relationships.json",
    "output_dataflow_md": "./docs/data_flow.md",
    "output_dataflow_json": "./docs/data_flow.json",
    "output_metrics_md": "./docs/business_metrics.md",
    "output_metrics_json": "./docs/business_metrics.json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Connect to AMI DB through JDBC and document SHOW TABLES output."
    )
    parser.add_argument("--driver-class", default=os.getenv("AMI_DB_DRIVER", DEFAULTS["driver_class"]))
    parser.add_argument("--url", default=os.getenv("AMI_DB_URL", DEFAULTS["url"]))
    parser.add_argument("--user", default=os.getenv("AMI_DB_USER", DEFAULTS["user"]))
    parser.add_argument("--password", default=os.getenv("AMI_DB_PASSWORD"))
    parser.add_argument("--jar-path", default=os.getenv("AMI_DB_JAR", DEFAULTS["jar_path"]))
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


def connect_db(
    driver_class: str,
    url: str,
    user: str,
    password: str,
    jar_path: str,
    java_home: str,
) -> list[tuple[Any, ...]]:
    jar_abs = str(Path(jar_path).resolve())
    if not Path(jar_abs).exists():
        raise FileNotFoundError(f"JDBC jar not found: {jar_abs}")

    ensure_jvm(java_home=java_home, classpath=[jar_abs])

    return jaydebeapi.connect(driver_class, url, [user, password])


def fetch_show_tables(cursor: Any) -> list[tuple[Any, ...]]:
    cursor.execute("show tables")
    rows = cursor.fetchall()
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


def build_table_records(rows: list[list[Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
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


def write_dashboard(path: Path, payload: dict[str, Any]) -> None:
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
                        for row in payload["rows"]
                ],
        }
        dashboard_json = json.dumps(dashboard_data, ensure_ascii=True)

        html = """<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>DB Tables Dashboard</title>
    <style>
        :root {
            --bg: #f7efe4;
            --card: #fffdf8;
            --ink: #2c221a;
            --muted: #6f6052;
            --accent: #0d7f6f;
            --accent-2: #ea6a47;
            --line: #eadcca;
            --shadow: 0 8px 20px rgba(45, 31, 20, 0.08);
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, sans-serif;
            color: var(--ink);
            background:
                radial-gradient(1200px 600px at -10% -10%, #f9c88a55, transparent),
                radial-gradient(1000px 500px at 120% 0%, #8fd6cb55, transparent),
                var(--bg);
        }

        .wrap {
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }

        .hero {
            background: linear-gradient(135deg, #1a9c87, #0b6f61);
            color: #fff;
            border-radius: 16px;
            padding: 20px;
            box-shadow: var(--shadow);
        }

        .hero h1 {
            margin: 0 0 8px;
            font-size: 28px;
            letter-spacing: 0.2px;
        }

        .hero p {
            margin: 4px 0;
            opacity: 0.92;
        }

        .kpis {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-top: 16px;
        }

        .card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 14px;
            box-shadow: var(--shadow);
        }

        .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.8px; }
        .value { font-size: 28px; font-weight: 700; margin-top: 6px; }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 14px;
        }

        .chart-title { margin: 0 0 10px; font-size: 16px; }

        .bar-row { display: grid; grid-template-columns: 130px 1fr 40px; gap: 10px; align-items: center; margin: 8px 0; }
        .bar-wrap { height: 10px; background: #f3e7d8; border-radius: 999px; overflow: hidden; }
        .bar { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }
        .bar-name { font-size: 13px; color: var(--muted); }
        .bar-num { font-size: 13px; font-weight: 600; text-align: right; }

        .tools {
            display: flex;
            gap: 10px;
            margin-top: 12px;
            flex-wrap: wrap;
        }

        input, select {
            height: 38px;
            border-radius: 10px;
            border: 1px solid var(--line);
            background: #fff;
            color: var(--ink);
            padding: 0 10px;
            min-width: 180px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }

        th, td {
            border-bottom: 1px solid #f2e7d8;
            padding: 10px;
            text-align: left;
            font-size: 13px;
            vertical-align: top;
        }

        th {
            background: #f8f1e8;
            position: sticky;
            top: 0;
            z-index: 1;
        }

        tr:hover td { background: #fff8ee; }

        .pill {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 999px;
            font-size: 12px;
            background: #edf7f5;
            color: #0f6659;
            border: 1px solid #c8e5de;
        }

        .muted { color: var(--muted); font-size: 12px; }

        @media (max-width: 980px) {
            .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .grid { grid-template-columns: 1fr; }
            th, td { font-size: 12px; }
        }
    </style>
</head>
<body>
    <div class=\"wrap\">
        <section class=\"hero\">
            <h1>Database Tables Dashboard</h1>
            <p id=\"source\"></p>
            <p id=\"generated\"></p>
        </section>

        <section class=\"kpis\" id=\"kpis\"></section>

        <section class=\"grid\">
            <div class=\"card\">
                <h3 class=\"chart-title\">Tables by Owner</h3>
                <div id=\"ownerBars\"></div>
            </div>
            <div class=\"card\">
                <h3 class=\"chart-title\">Largest Tables by Row Estimate</h3>
                <div id=\"largestBars\"></div>
            </div>
        </section>

        <section class=\"card\" style=\"margin-top:12px;\">
            <div class=\"tools\">
                <input id=\"search\" placeholder=\"Search by table name\" />
                <select id=\"ownerFilter\"></select>
                <select id=\"policyFilter\"></select>
            </div>
            <p class=\"muted\" id=\"countText\"></p>
            <div style=\"overflow:auto; max-height: 70vh;\">
                <table>
                    <thead>
                        <tr>
                            <th>Table</th>
                            <th>Owner</th>
                            <th>Policy</th>
                            <th>Scope</th>
                            <th>Rows</th>
                            <th>Columns</th>
                            <th>Realtime</th>
                        </tr>
                    </thead>
                    <tbody id=\"rows\"></tbody>
                </table>
            </div>
        </section>
    </div>

    <script>
        const data = __DASHBOARD_DATA__;
        const tables = data.tables || [];

        const fmt = (v) => {
            if (v === null || v === undefined) return "-";
            if (typeof v === "number") return v.toLocaleString();
            return String(v);
        };

        document.getElementById("source").textContent =
            "URL: " + data.url + " | User: " + data.user + " | Driver: " + data.driver_class;
        document.getElementById("generated").textContent =
            "Generated (UTC): " + data.generated_at_utc;

        const totalRows = tables.reduce((acc, t) => acc + (Number(t.row_estimate) || 0), 0);
        const avgCols = tables.length
            ? (tables.reduce((acc, t) => acc + (Number(t.column_count) || 0), 0) / tables.length).toFixed(1)
            : "0.0";
        const realtimeCount = tables.filter((t) => t.is_realtime === true).length;
        const systemCount = tables.filter((t) => String(t.owner || "").toUpperCase() === "SYSTEM").length;

        const kpiItems = [
            ["Total Tables", tables.length],
            ["Estimated Rows", totalRows.toLocaleString()],
            ["Realtime Tables", realtimeCount],
            ["System Tables", systemCount],
        ];

        const kpis = document.getElementById("kpis");
        for (const [label, value] of kpiItems) {
            const div = document.createElement("div");
            div.className = "card";
            div.innerHTML =
                '<div class="label">' + label + '</div><div class="value">' + value + '</div>';
            kpis.appendChild(div);
        }

        const countBy = (arr, key) => {
            const out = new Map();
            for (const item of arr) {
                const k = String(item[key] ?? "UNKNOWN");
                out.set(k, (out.get(k) || 0) + 1);
            }
            return Array.from(out.entries()).sort((a, b) => b[1] - a[1]);
        };

        const renderBars = (elId, rows) => {
            const max = rows.reduce((m, r) => Math.max(m, r[1]), 1);
            const parent = document.getElementById(elId);
            parent.innerHTML = "";
            for (const [name, val] of rows) {
                const row = document.createElement("div");
                row.className = "bar-row";
                row.innerHTML =
                    '<div class="bar-name">' + name + '</div>' +
                    '<div class="bar-wrap"><div class="bar" style="width:' + Math.max(4, (val / max) * 100).toFixed(1) + '%"></div></div>' +
                    '<div class="bar-num">' + val + '</div>';
                parent.appendChild(row);
            }
        };

        const owners = countBy(tables, "owner");
        renderBars("ownerBars", owners);

        const biggest = [...tables]
            .sort((a, b) => (Number(b.row_estimate) || 0) - (Number(a.row_estimate) || 0))
            .slice(0, 10)
            .map((t) => [t.name, Number(t.row_estimate) || 0]);
        renderBars("largestBars", biggest);

        const ownerFilter = document.getElementById("ownerFilter");
        const policyFilter = document.getElementById("policyFilter");
        const search = document.getElementById("search");
        const tbody = document.getElementById("rows");
        const countText = document.getElementById("countText");

        const uniqueOwners = ["ALL", ...new Set(tables.map((t) => String(t.owner ?? "UNKNOWN")))].sort();
        const uniquePolicies = ["ALL", ...new Set(tables.map((t) => String(t.change_policy ?? "UNKNOWN")))].sort();

        ownerFilter.innerHTML = uniqueOwners.map((o) => '<option value="' + o + '">Owner: ' + o + '</option>').join("");
        policyFilter.innerHTML = uniquePolicies.map((p) => '<option value="' + p + '">Policy: ' + p + '</option>').join("");

        const renderTable = () => {
            const s = search.value.trim().toLowerCase();
            const owner = ownerFilter.value;
            const policy = policyFilter.value;

            const filtered = tables.filter((t) => {
                const matchSearch = !s || String(t.name || "").toLowerCase().includes(s);
                const matchOwner = owner === "ALL" || String(t.owner ?? "UNKNOWN") === owner;
                const matchPolicy = policy === "ALL" || String(t.change_policy ?? "UNKNOWN") === policy;
                return matchSearch && matchOwner && matchPolicy;
            });

            countText.textContent = "Showing " + filtered.length + " of " + tables.length + " tables | Avg columns: " + avgCols;
            tbody.innerHTML = filtered
                .map((t) => {
                    const realtime = t.is_realtime === null ? "-" : (t.is_realtime ? "Yes" : "No");
                    return (
                        "<tr>" +
                        "<td><strong>" + fmt(t.name) + "</strong></td>" +
                        "<td><span class='pill'>" + fmt(t.owner) + "</span></td>" +
                        "<td>" + fmt(t.change_policy) + "</td>" +
                        "<td>" + fmt(t.scope) + "</td>" +
                        "<td>" + fmt(t.row_estimate) + "</td>" +
                        "<td>" + fmt(t.column_count) + "</td>" +
                        "<td>" + realtime + "</td>" +
                        "</tr>"
                    );
                })
                .join("");
        };

        search.addEventListener("input", renderTable);
        ownerFilter.addEventListener("change", renderTable);
        policyFilter.addEventListener("change", renderTable);
        renderTable();
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


def main() -> int:
    args = parse_args()
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
    try:
        connection = connect_db(
            driver_class=args.driver_class,
            url=args.url,
            user=args.user,
            password=args.password,
            jar_path=args.jar_path,
            java_home=args.java_home,
        )
        cursor = connection.cursor()
        rows = fetch_show_tables(cursor)
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

    write_markdown(output_md, payload)
    write_json(output_json, payload)
    write_dashboard(output_dashboard, payload)
    write_schema_markdown(output_schema_md, logic_payload)
    write_relationships_markdown(output_relationships_md, logic_payload)
    write_dataflow_markdown(output_dataflow_md, logic_payload)
    write_metrics_markdown(output_metrics_md, logic_payload)
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

    print(f"Wrote {len(rows)} tables to {output_md}")
    print(f"Wrote JSON payload to {output_json}")
    print(f"Wrote dashboard to {output_dashboard}")
    print(f"Wrote schema catalog to {output_schema_md} and {output_schema_json}")
    print(
        f"Wrote relationship candidates to {output_relationships_md} and {output_relationships_json}"
    )
    print(f"Wrote data flow classification to {output_dataflow_md} and {output_dataflow_json}")
    print(f"Wrote business metrics to {output_metrics_md} and {output_metrics_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
