#!/usr/bin/env python3
"""Generate first-pass documentation for AMI DB tables using JDBC."""

from __future__ import annotations

import argparse
import json
import os
import sys
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


def fetch_show_tables(
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

    connection = None
    cursor = None
    try:
        connection = jaydebeapi.connect(driver_class, url, [user, password])
        cursor = connection.cursor()
        cursor.execute("show tables")
        rows = cursor.fetchall()
        return sorted(rows, key=lambda row: str(row[0]).lower())
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


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


def main() -> int:
    args = parse_args()
    if not args.password:
        print(
            "Missing password. Pass --password or set AMI_DB_PASSWORD.",
            file=sys.stderr,
        )
        return 2

    rows = fetch_show_tables(
        driver_class=args.driver_class,
        url=args.url,
        user=args.user,
        password=args.password,
        jar_path=args.jar_path,
        java_home=args.java_home,
    )

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

    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_dashboard = Path(args.output_dashboard)
    write_markdown(output_md, payload)
    write_json(output_json, payload)
    write_dashboard(output_dashboard, payload)

    print(f"Wrote {len(rows)} tables to {output_md}")
    print(f"Wrote JSON payload to {output_json}")
    print(f"Wrote dashboard to {output_dashboard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
