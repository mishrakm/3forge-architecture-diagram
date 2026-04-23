# Database Tables

Generated at (UTC): 2026-04-23T06:57:08.306895+00:00

## Source

- URL: jdbc:amisql:125.125.126.5:3280
- User: pwadmin
- Driver: com.f1.ami.amidb.jdbc.AmiDbJdbcDriver
- Query: `show tables`

## Summary

- Total tables: 55

## Tables

| Table Name | Raw Metadata |
|---|---|
| __CENTER | `["__CENTER", 1, 250, "TEXT", "REJECT", "SYSTEM", "PUBLIC", 2, 4]` |
| __COLUMN | `["__COLUMN", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 1153, 7]` |
| __COMMAND | `["__COMMAND", 1, 250, null, "REJECT", "AMI", "PUBLIC", 0, 22]` |
| __CONNECTION | `["__CONNECTION", 1, 250, null, "REJECT", "AMI", "PUBLIC", 10, 11]` |
| __DATASOURCE | `["__DATASOURCE", 1, 250, "TEXT", "REJECT", "AMI", "PUBLIC", 3, 9]` |
| __DATASOURCE_TYPE | `["__DATASOURCE_TYPE", 1, 250, null, "REJECT", "AMI", "PUBLIC", 18, 5]` |
| __DBO | `["__DBO", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 0, 6]` |
| __INDEX | `["__INDEX", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 20, 8]` |
| __PLUGIN | `["__PLUGIN", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 30, 4]` |
| __PROCEDURE | `["__PROCEDURE", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 22, 6]` |
| __PROPERTY | `["__PROPERTY", 1, 250, null, "REJECT", "AMI", "PUBLIC", 0, 2]` |
| __RELAY | `["__RELAY", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 1, 7]` |
| __REPLICATION | `["__REPLICATION", 1, 250, "TEXT", "REJECT", "SYSTEM", "PUBLIC", 5, 6]` |
| __RESOURCE | `["__RESOURCE", 1, 250, null, "REJECT", "AMI", "PUBLIC", 0, 6]` |
| __STATS | `["__STATS", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 1329, 11]` |
| __TABLE | `["__TABLE", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 55, 7]` |
| __TIMER | `["__TIMER", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 2, 9]` |
| __TRIGGER | `["__TRIGGER", 1, 250, null, "REJECT", "SYSTEM", "PUBLIC", 14, 7]` |
| BuySells | `["BuySells", 0, 100, null, "REJECT", "USER", "PUBLIC", 14116, 22]` |
| BuySellsAgg | `["BuySellsAgg", 0, 100, null, "REJECT", "USER", "PUBLIC", 2798, 26]` |
| BuySellsAggC1 | `["BuySellsAggC1", 0, 100, null, "REJECT", "USER", "PUBLIC", 2877, 27]` |
| BuySellsAggC2 | `["BuySellsAggC2", 0, 100, null, "REJECT", "USER", "PUBLIC", 2798, 27]` |
| conrevNetBookDelta | `["conrevNetBookDelta", 1, 100, null, "REJECT", "USER", "PUBLIC", 79, 43]` |
| GroupedPnl | `["GroupedPnl", 1, 3000, null, "REJECT", "USER", "PUBLIC", 20, 4]` |
| IV_GDBD | `["IV_GDBD", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 10]` |
| MasterExpenseParams | `["MasterExpenseParams", 0, 100, null, "REJECT", "USER", "PUBLIC", 10, 5]` |
| MasterTraderIds | `["MasterTraderIds", 0, 100, null, "REJECT", "USER", "PUBLIC", 169, 3]` |
| NetBook | `["NetBook", 1, 100, null, "REJECT", "USER", "PUBLIC", 2798, 37]` |
| NetBookC | `["NetBookC", 1, 100, null, "REJECT", "USER", "PUBLIC", 2798, 40]` |
| NetBookGrouped | `["NetBookGrouped", 0, 100, null, "REJECT", "USER", "PUBLIC", 104, 8]` |
| NetBookGroupedFiltered | `["NetBookGroupedFiltered", 0, 100, null, "REJECT", "USER", "PUBLIC", 102, 8]` |
| NetBookSnap | `["NetBookSnap", 1, 1000, null, "REJECT", "USER", "PUBLIC", 58513, 37]` |
| NetBookSnap2 | `["NetBookSnap2", 1, 1000, null, "REJECT", "USER", "PUBLIC", 0, 36]` |
| NetPnl | `["NetPnl", 1, 3000, null, "REJECT", "USER", "PUBLIC", 1, 2]` |
| nse_tbt_snap | `["nse_tbt_snap", 0, 100, null, "ADD", "USER", "PUBLIC", 1735, 39]` |
| order_msgs_noxml | `["order_msgs_noxml", 1, 100, null, "ADD", "USER", "PUBLIC", 14116, 30]` |
| order_msgs_noxml_clean | `["order_msgs_noxml_clean", 0, 100, null, "ADD", "USER", "PUBLIC", 14116, 30]` |
| ResultSet | `["ResultSet", 0, 100, null, "REJECT", "USER", "PUBLIC", 107269, 29]` |
| ServerUsers | `["ServerUsers", 0, 100, null, "REJECT", "USER", "PUBLIC", 110, 13]` |
| SquaredOff | `["SquaredOff", 1, 100, null, "ADD", "USER", "PUBLIC", 0, 32]` |
| SquareOff | `["SquareOff", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 35]` |
| TRADEBOOK | `["TRADEBOOK", null, null, "HISTORICAL", null, "USER", "PUBLIC", 4648877, 45]` |
| TradeBook | `["TradeBook", 1, 100, null, "ADD", "USER", "PUBLIC", 14116, 44]` |
| TradeBook_TID | `["TradeBook_TID", 0, 100, null, "REJECT", "USER", "PUBLIC", 14116, 44]` |
| TradeSummary | `["TradeSummary", 1, 100, null, "REJECT", "USER", "PUBLIC", 104, 7]` |
| U1_NetBook | `["U1_NetBook", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 35]` |
| U2_BuySellsAgg | `["U2_BuySellsAgg", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 26]` |
| U2_conrevNetBookDelta | `["U2_conrevNetBookDelta", 0, 100, null, "REJECT", "USER", "PUBLIC", 0, 43]` |
| U2_NetBook | `["U2_NetBook", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 35]` |
| U2_NetBookConrev | `["U2_NetBookConrev", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 40]` |
| U3_BuySellsAgg | `["U3_BuySellsAgg", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 26]` |
| U3_conrevNetBookDelta | `["U3_conrevNetBookDelta", 0, 100, null, "REJECT", "USER", "PUBLIC", 0, 43]` |
| U3_NetBook | `["U3_NetBook", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 35]` |
| U3_NetBookConrev | `["U3_NetBookConrev", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 40]` |
| VC3_GDBD | `["VC3_GDBD", 1, 100, null, "REJECT", "USER", "PUBLIC", 0, 10]` |
