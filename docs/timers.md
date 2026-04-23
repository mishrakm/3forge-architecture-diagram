# Timers

Generated at (UTC): 2026-04-23T06:57:08.306895+00:00

Timer count: 2

| Timer | Type | Priority | Schedule | Enabled |
|---|---|---|---|---|
| B2D_NSE_1600 | AMISCRIPT | 0 | 0 0 16 * * * IST | True |
| NetBookSnap | AMISCRIPT | 0 | */20 * 9-15 * * MON-SUN IST | True |

## Timer Definitions

### B2D_NSE_1600

- Type: AMISCRIPT
- Priority: 0
- Schedule: 0 0 16 * * * IST
- Owner: USER
- Last run time: None
- Next run time: 2026-04-23 16:00:00
- Enabled: True

```sql
CREATE TIMER B2D_NSE_1600 OFTYPE AMISCRIPT ON "0 0 16 * * * IST" PRIORITY 0 USE limit="9999999999999" logging="verbose" script="insert into TRADEBOOK select formatDate(timestamp(),\"yyyyMMdd\",\"IST\") as Date,* from TradeBook where Exch==\"NSE\"" timeout="10800000";
```

### NetBookSnap

- Type: AMISCRIPT
- Priority: 0
- Schedule: */20 * 9-15 * * MON-SUN IST
- Owner: USER
- Last run time: 2026-04-23 12:27:00
- Next run time: 2026-04-23 12:27:20
- Enabled: True

```sql
CREATE TIMER NetBookSnap OFTYPE AMISCRIPT ON "*/20 * 9-15 * * MON-SUN IST" PRIORITY 0 USE logging="verbose" script="CALL netBookSnap();";
```

