# AMI Flow Viewer

## DB Documentation Script

The project includes a starter script to document database tables via JDBC.

Requirements:
- Python packages: `jaydebeapi`, `JPype1`
- Java 17+
- JDBC driver jar at `./out.jar`

Run:

```bash
cd /home/projects/3forge-db-manager
export AMI_DB_PASSWORD='your-password'
/home/projects/3forge-db-manager/.venv/bin/python scripts/document_tables.py
```

Outputs:
- `docs/generated/tables.md` (human-readable table catalog)
- `docs/generated/tables.json` (raw machine-readable payload)
- `web/tables_dashboard.html` (unified browser dashboard: tables, schema, relationships, data flow, metrics, external mappings, trigger flow)
- `docs/generated/schema_catalog.md` and `docs/generated/schema_catalog.json` (column-level schema docs)
- `docs/generated/relationships.md` and `docs/generated/relationships.json` (inferred table relationships)
- `docs/generated/data_flow.md` and `docs/generated/data_flow.json` (data-flow category mapping)
- `docs/generated/business_metrics.md` and `docs/generated/business_metrics.json` (metric candidates + formula hints)
- `docs/generated/external_mappings.md` and `docs/generated/external_mappings.json` (centers + replications external mappings)
- `docs/generated/triggers.md` and `docs/generated/triggers.json` (trigger definitions and input->output flow)
- `docs/generated/procedures.md` and `docs/generated/procedures.json` (procedure inventory + definitions)
- `docs/generated/timers.md` and `docs/generated/timers.json` (timer inventory, schedules, and definitions)

## Multi-Instance AMI Flow Viewer

Use a JSON config to aggregate many AMI instances (up to 20 by default) in one page with a left tree and right detail pane.

Run:

```bash
cd /home/projects/3forge-db-manager
AMI_DB_PASSWORD='pwadmin123' /home/projects/3forge-db-manager/.venv/bin/python scripts/document_tables.py \
	--instances-config ./instances.json \
	--output-multi-dashboard ./web/ami_flow_viewer.html \
	--output-multi-json ./docs/generated/ami_flow_viewer.json
```

Open:
- `http://localhost:8080/ami_flow_viewer.html`

Config format (`instances.json`):

```json
{
	"instances": [
		{
			"name": "prod-main",
			"url": "jdbc:amisql:125.125.126.5:3280",
			"user": "pwadmin",
			"password_env": "AMI_DB_PASSWORD",
			"jar_path": "./out.jar"
		}
	]
}
```

## Local CORS Server (for browser view)

If you want to open dashboard assets through HTTP with permissive CORS headers:

```bash
cd /home/projects/3forge-db-manager
/home/projects/3forge-db-manager/.venv/bin/python scripts/cors_server.py --port 8080 --dir web
```

Then open:
- `http://localhost:8080/tables_dashboard.html`

## Live AMI Viewer (On-Click Real-Time Queries)

Use this mode when you want the dashboard to query AMI on-demand for each click (tables, triggers, procedures, timers, relationships, data flow, metrics, and external mappings).

Run:

```bash
cd /home/projects/3forge-db-manager
export AMI_DB_PASSWORD='your-password'
/home/projects/3forge-db-manager/.venv/bin/python scripts/live_view_server.py \
	--port 8080 \
	--dir web \
	--instances-config ./instances.json
```

Open:
- `http://localhost:8080/ami_flow_live.html`
- `http://localhost:8080/`

Notes:
- The site root now redirects to `ami_flow_live.html`, so opening `http://localhost:8080/` lands on the live viewer.
- `ami_flow_live.html` fetches data from `/api/*` on each click, so it stays connected to AMI in real time.
- Existing documentation generation (`scripts/document_tables.py`) remains unchanged for snapshot/export use cases.

This server adds:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

## One-Command Dashboard Launcher

Run data refresh + CORS server together:

```bash
cd /home/projects/3forge-db-manager
AMI_DB_PASSWORD='pwadmin123' ./scripts/bin/start_dashboard.sh
```

Open:
- `http://localhost:8080/tables_dashboard.html`

Options:
- `PORT=8090 ./scripts/bin/start_dashboard.sh` to change port.
- `SKIP_REFRESH=1 ./scripts/bin/start_dashboard.sh` to serve existing docs without querying DB.

Optional flags:

```bash
/home/projects/3forge-db-manager/.venv/bin/python scripts/document_tables.py \
	--url 'jdbc:amisql:125.125.126.5:3280' \
	--user 'pwadmin' \
	--password '***' \
	--jar-path './out.jar' \
	--output-md './docs/generated/tables.md' \
	--output-json './docs/generated/tables.json'
```
