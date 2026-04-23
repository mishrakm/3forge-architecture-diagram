# Relationship Candidates

Generated at (UTC): 2026-04-23T06:57:08.306895+00:00

Candidates found: 24

| Left Table | Right Table | Shared Keys | Strength |
|---|---|---|---|
| TRADEBOOK | TradeBook | algoid, brokerid, uid | 3 |
| TRADEBOOK | TradeBook_TID | algoid, brokerid, uid | 3 |
| TradeBook | TradeBook_TID | algoid, brokerid, uid | 3 |
| MasterExpenseParams | ServerUsers | id | 1 |
| MasterExpenseParams | SquareOff | id | 1 |
| MasterExpenseParams | SquaredOff | id | 1 |
| MasterExpenseParams | __COMMAND | id | 1 |
| ServerUsers | SquareOff | id | 1 |
| ServerUsers | SquaredOff | id | 1 |
| ServerUsers | __COMMAND | id | 1 |
| SquareOff | SquaredOff | id | 1 |
| SquareOff | __COMMAND | id | 1 |
| SquaredOff | __COMMAND | id | 1 |
| TRADEBOOK | order_msgs_noxml | algoid | 1 |
| TRADEBOOK | order_msgs_noxml_clean | algoid | 1 |
| TradeBook | order_msgs_noxml | algoid | 1 |
| TradeBook | order_msgs_noxml_clean | algoid | 1 |
| TradeBook_TID | order_msgs_noxml | algoid | 1 |
| TradeBook_TID | order_msgs_noxml_clean | algoid | 1 |
| U2_conrevNetBookDelta | U3_conrevNetBookDelta | leggroupid | 1 |
| U2_conrevNetBookDelta | conrevNetBookDelta | leggroupid | 1 |
| U3_conrevNetBookDelta | conrevNetBookDelta | leggroupid | 1 |
| __DATASOURCE | __RELAY | relayid | 1 |
| order_msgs_noxml | order_msgs_noxml_clean | algoid | 1 |
