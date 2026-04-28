# Data Flow Classification

Generated at (UTC): 2026-04-23T07:00:03.451392+00:00

| Table | Category | Owner | Storage Mode | Realtime | Upstream Hints |
|---|---|---|---|---|---|
| BuySells | core_operational | USER | None | False | BuySellsAgg, BuySellsAggC1, BuySellsAggC2, U2_BuySellsAgg, U3_BuySellsAgg |
| MasterExpenseParams | core_operational | USER | None | False |  |
| MasterTraderIds | core_operational | USER | None | False |  |
| order_msgs_noxml_clean | core_operational | USER | None | False |  |
| ServerUsers | core_operational | USER | None | False |  |
| TradeBook_TID | core_operational | USER | None | False |  |
| BuySellsAgg | derived_aggregate | USER | None | False | BuySells, BuySellsAggC1, BuySellsAggC2, U2_BuySellsAgg, U3_BuySellsAgg |
| BuySellsAggC1 | derived_aggregate | USER | None | False | BuySells, BuySellsAgg, BuySellsAggC2, U2_BuySellsAgg, U3_BuySellsAgg |
| BuySellsAggC2 | derived_aggregate | USER | None | False | BuySells, BuySellsAgg, BuySellsAggC1, U2_BuySellsAgg, U3_BuySellsAgg |
| conrevNetBookDelta | derived_aggregate | USER | None | True | U2_conrevNetBookDelta, U3_conrevNetBookDelta |
| GroupedPnl | derived_aggregate | USER | None | True |  |
| NetBookGrouped | derived_aggregate | USER | None | False | NetBook, NetBookC, NetBookGroupedFiltered, NetBookSnap, NetBookSnap2, U1_NetBook |
| NetBookGroupedFiltered | derived_aggregate | USER | None | False | NetBookGrouped |
| NetBookSnap | derived_aggregate | USER | None | True | NetBook, NetBookC, NetBookGrouped, NetBookGroupedFiltered, NetBookSnap2, U1_NetBook |
| NetBookSnap2 | derived_aggregate | USER | None | True |  |
| nse_tbt_snap | derived_aggregate | USER | None | False |  |
| ResultSet | derived_aggregate | USER | None | False |  |
| TradeSummary | derived_aggregate | USER | None | True | MasterTraderIds, TRADEBOOK, TradeBook, TradeBook_TID |
| U2_BuySellsAgg | derived_aggregate | USER | None | True | BuySells, BuySellsAgg, BuySellsAggC1, BuySellsAggC2, U3_BuySellsAgg |
| U2_conrevNetBookDelta | derived_aggregate | USER | None | False | U3_conrevNetBookDelta, conrevNetBookDelta |
| U3_BuySellsAgg | derived_aggregate | USER | None | True | BuySells, BuySellsAgg, BuySellsAggC1, BuySellsAggC2, U2_BuySellsAgg |
| U3_conrevNetBookDelta | derived_aggregate | USER | None | False | U2_conrevNetBookDelta, conrevNetBookDelta |
| TRADEBOOK | source_historical | USER | HISTORICAL | None | TradeBook_TID |
| IV_GDBD | streaming_live | USER | None | True |  |
| NetBook | streaming_live | USER | None | True | NetBookC, NetBookGrouped, NetBookGroupedFiltered, NetBookSnap, NetBookSnap2, U1_NetBook |
| NetBookC | streaming_live | USER | None | True | U2_NetBookConrev, U3_NetBookConrev |
| NetPnl | streaming_live | USER | None | True |  |
| order_msgs_noxml | streaming_live | USER | None | True | order_msgs_noxml_clean |
| SquaredOff | streaming_live | USER | None | True |  |
| SquareOff | streaming_live | USER | None | True |  |
| TradeBook | streaming_live | USER | None | True | TradeBook_TID |
| U1_NetBook | streaming_live | USER | None | True | NetBook, NetBookC, NetBookGrouped, NetBookGroupedFiltered, NetBookSnap, NetBookSnap2 |
| U2_NetBook | streaming_live | USER | None | True | NetBook, NetBookC, NetBookGrouped, NetBookGroupedFiltered, NetBookSnap, NetBookSnap2 |
| U2_NetBookConrev | streaming_live | USER | None | True | U3_NetBookConrev |
| U3_NetBook | streaming_live | USER | None | True | NetBook, NetBookC, NetBookGrouped, NetBookGroupedFiltered, NetBookSnap, NetBookSnap2 |
| U3_NetBookConrev | streaming_live | USER | None | True | U2_NetBookConrev |
| VC3_GDBD | streaming_live | USER | None | True |  |
| __CENTER | system | SYSTEM | TEXT | True |  |
| __COLUMN | system | SYSTEM | None | True |  |
| __COMMAND | system | AMI | None | True |  |
| __CONNECTION | system | AMI | None | True |  |
| __DATASOURCE | system | AMI | TEXT | True | __DATASOURCE_TYPE |
| __DATASOURCE_TYPE | system | AMI | None | True |  |
| __DBO | system | SYSTEM | None | True |  |
| __INDEX | system | SYSTEM | None | True |  |
| __PLUGIN | system | SYSTEM | None | True |  |
| __PROCEDURE | system | SYSTEM | None | True |  |
| __PROPERTY | system | AMI | None | True |  |
| __RELAY | system | SYSTEM | None | True |  |
| __REPLICATION | system | SYSTEM | TEXT | True |  |
| __RESOURCE | system | AMI | None | True |  |
| __STATS | system | SYSTEM | None | True |  |
| __TABLE | system | SYSTEM | None | True |  |
| __TIMER | system | SYSTEM | None | True |  |
| __TRIGGER | system | SYSTEM | None | True |  |

## Trigger Flow (Input -> Output)

| Trigger | Type | Inputs | Output | Enabled | Priority |
|---|---|---|---|---|---|
| CleanOrders | JOIN | order_msgs_noxml, ResultSet | order_msgs_noxml_clean | True | 0 |
| trgBuySells | JOIN | TradeBook_TID, MasterExpenseParams | BuySells | True | 0 |
| trgBuySellsAgg | AGGREGATE | BuySells | BuySellsAgg | True | 1 |
| trgBuySellsAggC1 | PROJECTION | conrevNetBookDelta, BuySellsAgg | BuySellsAggC1 | True | 0 |
| trgBuySellsAggC2 | AGGREGATE | BuySellsAggC1 | BuySellsAggC2 | True | 1 |
| trgGroupedPnl | AGGREGATE | NetBookC | GroupedPnl | True | 0 |
| trgMergeTraderId | JOIN | TradeBook, MasterTraderIds | TradeBook_TID | True | 0 |
| trgNetBook | JOIN | BuySellsAgg, nse_tbt_snap | NetBook | True | 2 |
| trgNetBookConRev | JOIN | BuySellsAggC2, nse_tbt_snap | NetBookC | True | 2 |
| trgNetBookGrouped | AGGREGATE | NetBookC | NetBookGrouped | True | 0 |
| trgNetBookGroupedFiltered | PROJECTION | NetBookGrouped | NetBookGroupedFiltered | True | 0 |
| trgNetPnL | AGGREGATE | NetBookGroupedFiltered | NetPnl | True | 0 |
| trgTradeBook | JOIN | order_msgs_noxml_clean, ServerUsers | TradeBook | True | 0 |
| trgTradeSum | AGGREGATE | TradeBook | TradeSummary | True | 0 |
