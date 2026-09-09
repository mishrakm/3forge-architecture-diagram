# Production deployment — 3Forge DB manager

AMI JDBC table/trigger/procedure browser and live viewer (formerly architecture-diagram). Dashboard on port **18092**.

## Where it runs

| Host | Path |
|---|---|
| 192.192.100.130 | `/home/projects/3forge-db-manager` |

Collation copy: `/home/production/apps/3forge-db-manager`.

## Dependencies

- Python 3 (project `.venv` or python3.13), `jaydebeapi`, JPype
- Java 17+, `out.jar`
- `instances.json` (gitignored; example: `instances.example.json`). Live copy also under `deploy/130.instances.json`.

## Install

```bash
cp -a /home/production/apps/3forge-db-manager /home/projects/3forge-db-manager
cd /home/projects/3forge-db-manager
cp deploy/130.instances.json instances.json
./bin/start.sh
```

Open `http://<host>:18092/`.
