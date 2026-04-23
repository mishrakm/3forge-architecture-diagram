# Schema Catalog

Generated at (UTC): 2026-04-23T05:51:04.482251+00:00

Total tables with schema: 55

## __CENTER

- Columns: 4

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| CenterName | String | False |  |
| Url | String | False |  |
| CertFile | String | False |  |
| Password | String | False |  |

## __COLUMN

- Columns: 7

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| TableName | String | False |  |
| ColumnName | String | False |  |
| DataType | Enum | False |  |
| Options | Enum | False |  |
| NoNull | Boolean | False |  |
| Position | Integer | False |  |
| DefinedBy | Enum | True | NoNull |

## __COMMAND

- Columns: 22

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| CI | Integer | False |  |
| RI | Long | False |  |
| ID | String | False |  |
| AR | String | False |  |
| PR | Integer | False |  |
| NA | String | False |  |
| FL | String | False |  |
| WH | String | False |  |
| HP | String | False |  |
| SM | String | False |  |
| CB | Integer | False |  |
| AmiScript | String | False |  |
| N | Enum | False |  |
| S | String | False |  |
| L | Integer | False |  |
| F | String | False |  |
| I | String | False |  |
| P | Enum | False |  |
| V | Integer | False |  |
| M | Long | False |  |
| D | Long | False |  |
| C | Long | False |  |

## __CONNECTION

- Columns: 11

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| AI | Enum | False |  |
| EC | Long | False |  |
| CI | Long | False |  |
| MA | Long | False |  |
| MC | Long | False |  |
| O | String | False |  |
| PL | String | False |  |
| RI | String | False |  |
| RP | Long | False |  |
| RH | String | False |  |
| CT | Long | False |  |

## __DATASOURCE

- Columns: 9

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| NM | String | True | NoNull |
| AD | String | True | NoNull |
| UR | String | False |  |
| US | String | False |  |
| PW | String | False |  |
| Password | String | False |  |
| OP | String | False |  |
| RelayId | String | False |  |
| PermittedOverrides | String | False |  |

## __DATASOURCE_TYPE

- Columns: 5

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| Description | String | False |  |
| I | String | False |  |
| ClassType | String | False |  |
| Icon | String | False |  |
| Properties | String | False |  |

## __DBO

- Columns: 6

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| DboName | String | True | NoNull |
| DboType | String | True | NoNull |
| Priority | String | True | NoNull |
| Options | String | False |  |
| DefinedBy | Enum | True | NoNull |
| Enabled | Boolean | True | NoNull |

## __INDEX

- Columns: 8

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| IndexName | String | True | NoNull |
| TableName | String | True | NoNull |
| ColumnName | String | True | NoNull |
| IndexType | Enum | True | NoNull |
| IndexPosition | String | True | NoNull |
| Constraint | Enum | True | NoNull |
| AutoGen | Enum | True | NoNull |
| DefinedBy | Enum | True | NoNull |

## __PLUGIN

- Columns: 4

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| PluginName | String | True | NoNull |
| PluginType | Enum | True | NoNull |
| ClassType | String | True | NoNull |
| Arguments | String | False |  |

## __PROCEDURE

- Columns: 6

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| ProcedureName | String | True | NoNull |
| ProcedureType | String | True | NoNull |
| ReturnType | String | True | NoNull |
| Arguments | String | True | NoNull |
| Options | String | False |  |
| DefinedBy | Enum | True | NoNull |

## __PROPERTY

- Columns: 2

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| PropertyName | String | False |  |
| PropertyValue | String | False |  |

## __RELAY

- Columns: 7

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| MachineUid | String | True | NoNull |
| ProcessUid | String | False |  |
| StartTime | UTC | True | NoNull |
| ServerPort | Integer | False |  |
| RelayId | String | False |  |
| Hostname | String | False |  |
| ConnectTime | UTC | True | NoNull |

## __REPLICATION

- Columns: 6

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| ReplicationName | String | False |  |
| TargetTable | String | False |  |
| SourceCenter | String | False |  |
| SourceTable | String | False |  |
| Mapping | String | False |  |
| Options | String | False |  |

## __RESOURCE

- Columns: 6

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| I | String | False |  |
| ModifiedOn | Long | False |  |
| Checksum | Long | False |  |
| FileSize | Long | False |  |
| ImageWidth | Long | False |  |
| ImageHeight | Long | False |  |

## __STATS

- Columns: 11

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| Time | UTC | False |  |
| E | Long | False |  |
| UsedMemory | Long | False |  |
| MaxMemory | Long | False |  |
| PostGcUsedMemory | Long | False |  |
| RunningThreads | Short | False |  |
| Rows | Long | False |  |
| Events | Long | False |  |
| Queries | Long | False |  |
| UniqueUsers | Short | False |  |
| MaxUsers | Short | False |  |

## __TABLE

- Columns: 7

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| TableName | String | True | NoNull |
| Broadcast | Boolean | True | NoNull |
| RefreshPeriodMs | Long | False |  |
| PersistEngine | Enum | False |  |
| OnUndefColumn | Enum | True | NoNull |
| DefinedBy | Enum | True | NoNull |
| InitialCapacity | Integer | True | NoNull |

## __TIMER

- Columns: 9

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| TimerName | String | True | NoNull |
| TimerType | String | True | NoNull |
| Priority | String | True | NoNull |
| Schedule | String | True | NoNull |
| Options | String | False |  |
| DefinedBy | Enum | True | NoNull |
| LastRunTime | UTC | False |  |
| NextRunTime | UTC | False |  |
| Enabled | Boolean | True | NoNull |

## __TRIGGER

- Columns: 7

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| TriggerName | String | True | NoNull |
| TableName | String | True | NoNull |
| TriggerType | String | True | NoNull |
| Priority | String | True | NoNull |
| Options | String | False |  |
| DefinedBy | Enum | True | NoNull |
| Enabled | Boolean | True | NoNull |

## BuySells

- Columns: 22

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| BExpense | Double | False |  |
| SExpense | Double | False |  |
| NetBook | String | False | BITMAP |
| TraderId | Long | False |  |

## BuySellsAgg

- Columns: 26

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| Expense | Double | False |  |
| NetBook | String | False | BITMAP |
| TraderId | Long | False |  |

## BuySellsAggC1

- Columns: 27

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| Expense | Double | False |  |
| NetBook | String | False | BITMAP |
| TraderId | Long | False |  |
| AlgoBPL | Double | False |  |

## BuySellsAggC2

- Columns: 27

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| Expense | Double | False |  |
| NetBook | String | False | BITMAP |
| TraderId | Long | False |  |
| AlgoBPL | Double | False |  |

## conrevNetBookDelta

- Columns: 43

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| PfNo | Integer | False |  |
| Exch | String | False | BITMAP |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| SellAvg | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| FLTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |
| NetBook | String | False | BITMAP |
| RunTs | String | False | BITMAP |
| LegGroupId | String | False | BITMAP |
| LegRole | String | False | BITMAP |
| LegSignal | String | False | BITMAP |
| LegDiff | Double | False |  |
| LegQty | Long | False |  |
| TraderId | Long | False |  |

## GroupedPnl

- Columns: 4

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False |  |
| Positions | Double | False |  |
| PNL | Double | False |  |
| tt | Integer | False |  |

## IV_GDBD

- Columns: 10

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| rundate | String | False |  |
| Symbol | String | False |  |
| GoodDays | Integer | False |  |
| GDP | Double | False |  |
| BadDays | Integer | False |  |
| VeryBadDays | Integer | False |  |
| BDL | Double | False |  |
| LossPer | Double | False |  |
| PriorityScore | Double | False |  |
| PNL | Double | False |  |

## MasterExpenseParams

- Columns: 5

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| id | Integer | False |  |
| Exchange | String | False |  |
| InstType | String | False |  |
| Side | String | False |  |
| ExpPer | Float | False |  |

## MasterTraderIds

- Columns: 3

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| TraderID | Integer | False |  |
| backend | String | False |  |
| groupingId | Integer | False |  |

## NetBook

- Columns: 37

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| netBook | String | False | BITMAP |
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| PfNo | Integer | False |  |
| Exch | String | False | BITMAP |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| SellAvg | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| FLTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |
| TraderId | Long | False |  |

## NetBookC

- Columns: 40

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| netBook | String | False | BITMAP |
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| PfNo | Integer | False |  |
| Exch | String | False | BITMAP |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| SellAvg | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| FLTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |
| TraderId | Long | False |  |
| AlgoBPL | Double | False |  |
| TradeBPL | Double | False |  |
| TotalBPL | Double | False |  |

## NetBookGrouped

- Columns: 8

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Positions | Double | False |  |
| PNL | Double | False |  |
| Expense | Double | False |  |

## NetBookGroupedFiltered

- Columns: 8

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Positions | Double | False |  |
| PNL | Double | False |  |
| tt | Integer | False |  |

## NetBookSnap

- Columns: 37

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| snapTime | Long | False |  |
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False | BITMAP |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False |  |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| FLTP | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |
| TraderId | Long | False |  |

## NetBookSnap2

- Columns: 36

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| snapTime | Long | False |  |
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False | BITMAP |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False |  |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| FLTP | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |

## NetPnl

- Columns: 2

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| netPNL | Double | False |  |
| tt | Integer | False |  |

## nse_tbt_snap

- Columns: 39

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| Token | Integer | False |  |
| Ask1 | Double | False |  |
| AskQty1 | Integer | False |  |
| Ask2 | Double | False |  |
| AskQty2 | Integer | False |  |
| Ask3 | Double | False |  |
| AskQty3 | Integer | False |  |
| Ask4 | Double | False |  |
| AskQty4 | Integer | False |  |
| Ask5 | Double | False |  |
| AskQty5 | Integer | False |  |
| Bid1 | Double | False |  |
| BidQty1 | Integer | False |  |
| Bid2 | Double | False |  |
| BidQty2 | Integer | False |  |
| Bid3 | Double | False |  |
| BidQty3 | Integer | False |  |
| Bid4 | Double | False |  |
| BidQty4 | Integer | False |  |
| Bid5 | Double | False |  |
| BidQty5 | Integer | False |  |
| LTP | Integer | False |  |
| LTQ | Integer | False |  |
| LTT | Integer | False |  |
| Exch | Integer | False |  |
| PAsk1 | Double | False |  |
| PLTP | Integer | False |  |
| PAskQty1 | Integer | False |  |
| PBid1 | Double | False |  |
| PBidQty1 | Integer | False |  |
| upperb | Double | False |  |
| lowerb | Double | False |  |
| gVega | Double | False |  |
| gTheta | Double | False |  |
| gGamma | Double | False |  |
| gDelta | Double | False |  |
| gRho | Double | False |  |
| gIV | Double | False |  |
| fairprice | Double | False |  |

## order_msgs_noxml

- Columns: 30

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| UserIdenti | Long | False |  |
| Symbol | String | False |  |
| FillNumber | Integer | False |  |
| ExchTime | String | False |  |
| Token | Long | False |  |
| ProClient | String | False |  |
| Side | String | False |  |
| ExchOrderNo | String | False |  |
| PfNo | Integer | False |  |
| OrderStatus | String | False |  |
| HOSTIP | String | False |  |
| OrderType | String | False |  |
| FillQty | Integer | False |  |
| OptType | String | False |  |
| Expiry | String | False |  |
| ActualQty | Integer | False |  |
| SystemTime | String | False |  |
| Acc | String | False |  |
| AlgoId | Integer | False |  |
| StrikePrice | Double | False |  |
| ErrorMsg | String | False |  |
| InstType | String | False |  |
| Exchange | String | False |  |
| Price | Double | False |  |
| TraderId | Integer | False |  |
| FillPrice | Double | False |  |
| LeavesQty | Integer | False |  |
| NNF | Long | False |  |
| LastShare | Integer | False |  |
| A | String | False | BITMAP |

## order_msgs_noxml_clean

- Columns: 30

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| UserIdenti | Long | False |  |
| Symbol | String | False |  |
| FillNumber | Integer | False |  |
| ExchTime | String | False |  |
| Token | Long | False |  |
| ProClient | String | False |  |
| Side | String | False |  |
| ExchOrderNo | String | False |  |
| PfNo | Integer | False |  |
| OrderStatus | String | False |  |
| HOSTIP | String | False |  |
| OrderType | String | False |  |
| FillQty | Integer | False |  |
| OptType | String | False |  |
| Expiry | String | False |  |
| ActualQty | Integer | False |  |
| SystemTime | String | False |  |
| Acc | String | False |  |
| AlgoId | Integer | False |  |
| StrikePrice | Double | False |  |
| ErrorMsg | String | False |  |
| InstType | String | False |  |
| Exchange | String | False |  |
| Price | Double | False |  |
| TraderId | Integer | False |  |
| FillPrice | Double | False |  |
| LeavesQty | Integer | False |  |
| NNF | Long | False |  |
| LastShare | Integer | False |  |
| A | String | False | BITMAP |

## ResultSet

- Columns: 29

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| Exch | String | False | BITMAP |
| Segment | String | False | BITMAP |
| Token | Long | False |  |
| Symbol | String | False | BITMAP |
| ExpiryDate | String | False | BITMAP |
| InstType | String | False | BITMAP |
| OptionType | String | False | BITMAP |
| StrikePrice | Float | False |  |
| LotMultiple | Integer | False |  |
| LotSize | Double | False |  |
| TickSize | Double | False |  |
| Name | String | False | BITMAP |
| series | String | False | BITMAP |
| LowPriceRange | Double | False |  |
| HighPriceRange | Double | False |  |
| Trade | Integer | False |  |
| LowTR | Double | False |  |
| HighTR | Double | False |  |
| Divisor | Double | False |  |
| T1 | Integer | False |  |
| T2 | Integer | False |  |
| last_update_time | String | False | BITMAP |
| Freeze_Qty | Double | False |  |
| Unique_Token | Integer | False |  |
| ClosePrice | Double | False |  |
| ISIN | String | False |  |
| AssetToken | String | False |  |
| dedupe | Long | False |  |
| Expiry | String | False |  |

## ServerUsers

- Columns: 13

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| id | Integer | False |  |
| server | Integer | False |  |
| user | Integer | False |  |
| options | String | False |  |
| s_backend | String | False |  |
| s_user | String | False |  |
| s_group | Integer | False |  |
| s_groupname | String | False |  |
| s_name | String | False |  |
| s_frontend | String | False |  |
| s_msgline | Integer | False |  |
| s_minorders | Integer | False |  |
| NetBook | String | False | BITMAP |

## SquaredOff

- Columns: 32

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False |  |
| backend | String | False |  |
| ip | String | False |  |
| frontend | String | False |  |
| user | String | False |  |
| Acc | String | False |  |
| Exch | String | False |  |
| PfNo | Integer | False |  |
| Symbol | String | False |  |
| Expiry | String | False |  |
| StrikePrice | Float | False |  |
| OptType | String | False |  |
| InstType | String | False |  |
| NetValue | Float | False |  |
| NetPrice | Float | False |  |
| Expense | Float | False |  |
| NetBook | String | False |  |
| TraderId | Integer | False |  |
| ConsumableQty | Float | False |  |
| BuyQty | String | False |  |
| BuyPrice | String | False |  |
| BuyAvg | String | False |  |
| BuyValue | String | False |  |
| SellQty | Float | False |  |
| SellPrice | Float | False |  |
| SellAvg | Float | False |  |
| SellValue | Float | False |  |
| I | String | False |  |
| id | Integer | False |  |
| NetPosition | Integer | False |  |
| sent | Integer | False |  |
| adjusted | Integer | False |  |

## SquareOff

- Columns: 35

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| Expense | Double | False |  |
| NetBook | String | False | BITMAP |
| TraderId | Long | False |  |
| sent | Integer | False |  |
| NetQty | Long | False |  |
| Adjusted | Integer | False |  |
| AdjustedQty | Long | False |  |
| User | String | False | BITMAP |
| id | Long | False |  |
| ts | Long | False |  |
| adjusted | Integer | False |  |
| Qty | Double | False |  |

## TRADEBOOK

- Columns: 45

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| Date | String | True | None |
| server | String | True | None |
| user | String | True | None |
| sgroup | String | True | None |
| frontend | String | True | None |
| ip | String | True | None |
| UID | long | True | None |
| AutoNo | long | True | None |
| InOutTag | String | True | None |
| Exch | String | True | None |
| PfName | String | True | None |
| PfNo | Integer | True | None |
| Token | long | True | None |
| InstType | String | True | None |
| Symbol | String | True | None |
| Expiry | String | True | None |
| OptType | String | True | None |
| StrikePrice | double | True | None |
| ProClient | String | True | None |
| Acc | String | True | None |
| Side | String | True | None |
| ExchTimeStamp | String | True | None |
| SystemTimeStamp | String | True | None |
| OrderType | long | True | None |
| OrderStatus | String | True | None |
| Price | double | True | None |
| FillPrice | double | True | None |
| FillNumber | long | True | None |
| FillQty | long | True | None |
| LeavesQty | long | True | None |
| OrderNo | String | True | None |
| LastShare | long | True | None |
| ActualQty | long | True | None |
| ExchOrderNo | long | True | None |
| ErrorMsg | String | True | None |
| FilledLots | long | True | None |
| PAN | String | True | None |
| AlgoId | long | True | None |
| AlgoCategory | long | True | None |
| TradingSymbol | String | True | None |
| NNF | String | True | None |
| BrokerId | String | True | None |
| TraderId | long | True | None |
| LTP | double | True | None |
| NetBook | String | True | None |

## TradeBook

- Columns: 44

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| server | String | False | BITMAP |
| user | String | False | BITMAP |
| sgroup | String | False | BITMAP |
| frontend | String | False | BITMAP |
| ip | String | False | BITMAP |
| UID | Long | False |  |
| AutoNo | Long | False |  |
| InOutTag | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfName | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| InstType | String | False | BITMAP |
| Symbol | String | False | BITMAP |
| Expiry | String | False |  |
| OptType | String | False | BITMAP |
| StrikePrice | Float | False |  |
| ProClient | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Side | String | False | BITMAP |
| ExchTimeStamp | String | False |  |
| SystemTimeStamp | String | False |  |
| OrderType | Long | False |  |
| OrderStatus | String | False | BITMAP |
| Price | Double | False |  |
| FillPrice | Double | False |  |
| FillNumber | Long | False |  |
| FillQty | Long | False |  |
| LeavesQty | Long | False |  |
| OrderNo | String | False |  |
| LastShare | Long | False |  |
| ActualQty | Long | False |  |
| ExchOrderNo | Long | False |  |
| ErrorMsg | String | False |  |
| FilledLots | Long | False |  |
| PAN | String | False |  |
| AlgoId | Long | False |  |
| AlgoCategory | Long | False |  |
| TradingSymbol | String | False | BITMAP |
| NNF | String | False |  |
| BrokerId | String | False | BITMAP |
| TraderId | Long | False |  |
| LTP | Double | False |  |
| NetBook | String | False | BITMAP |

## TradeBook_TID

- Columns: 44

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| server | String | False | BITMAP |
| user | String | False | BITMAP |
| sgroup | String | False | BITMAP |
| frontend | String | False | BITMAP |
| ip | String | False | BITMAP |
| UID | Long | False |  |
| AutoNo | Long | False |  |
| InOutTag | String | False | BITMAP |
| Exch | String | False | BITMAP |
| PfName | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| InstType | String | False | BITMAP |
| Symbol | String | False | BITMAP |
| Expiry | String | False |  |
| OptType | String | False | BITMAP |
| StrikePrice | Float | False |  |
| ProClient | String | False | BITMAP |
| Acc | String | False | BITMAP |
| Side | String | False | BITMAP |
| ExchTimeStamp | String | False |  |
| SystemTimeStamp | String | False |  |
| OrderType | Long | False |  |
| OrderStatus | String | False | BITMAP |
| Price | Double | False |  |
| FillPrice | Double | False |  |
| FillNumber | Long | False |  |
| FillQty | Long | False |  |
| LeavesQty | Long | False |  |
| OrderNo | String | False |  |
| LastShare | Long | False |  |
| ActualQty | Long | False |  |
| ExchOrderNo | Long | False |  |
| ErrorMsg | String | False |  |
| FilledLots | Long | False |  |
| PAN | String | False |  |
| AlgoId | Long | False |  |
| AlgoCategory | Long | False |  |
| TradingSymbol | String | False | BITMAP |
| NNF | String | False |  |
| BrokerId | String | False | BITMAP |
| TraderId | Long | False |  |
| LTP | Double | False |  |
| NetBook | String | False | BITMAP |

## TradeSummary

- Columns: 7

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| server | String | False | BITMAP |
| user | String | False | BITMAP |
| sgroup | String | False | BITMAP |
| frontend | String | False | BITMAP |
| ip | String | False | BITMAP |
| buys | Long | False |  |
| sells | Long | False |  |

## U1_NetBook

- Columns: 35

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False |  |
| backend | String | False |  |
| ip | String | False |  |
| frontend | String | False |  |
| user | String | False |  |
| Acc | String | False |  |
| Exch | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False |  |
| StrikePrice | Long | False |  |
| OptType | String | False |  |
| InstType | String | False |  |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| FLTP | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |

## U2_BuySellsAgg

- Columns: 26

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False |  |
| backend | String | False |  |
| ip | String | False |  |
| frontend | String | False |  |
| user | String | False |  |
| Acc | String | False |  |
| Exch | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| NetBook | String | False |  |
| TraderId | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False |  |
| StrikePrice | Float | False |  |
| OptType | String | False |  |
| InstType | String | False |  |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| Expense | Double | False |  |

## U2_conrevNetBookDelta

- Columns: 43

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| PfNo | Integer | False |  |
| Exch | String | False | BITMAP |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| SellAvg | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| FLTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |
| NetBook | String | False | BITMAP |
| RunTs | String | False | BITMAP |
| LegGroupId | String | False | BITMAP |
| LegRole | String | False | BITMAP |
| LegSignal | String | False | BITMAP |
| LegDiff | Double | False |  |
| LegQty | Long | False |  |
| TraderId | Long | False |  |

## U2_NetBook

- Columns: 35

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False |  |
| backend | String | False |  |
| ip | String | False |  |
| frontend | String | False |  |
| user | String | False |  |
| Acc | String | False |  |
| Exch | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False |  |
| StrikePrice | Long | False |  |
| OptType | String | False |  |
| InstType | String | False |  |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| FLTP | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |

## U2_NetBookConrev

- Columns: 40

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| NetBook | String | False |  |
| sgroup | String | False |  |
| backend | String | False |  |
| ip | String | False |  |
| frontend | String | False |  |
| user | String | False |  |
| Acc | String | False |  |
| Exch | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False |  |
| StrikePrice | Float | False |  |
| OptType | String | False |  |
| TraderId | Long | False |  |
| InstType | String | False |  |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| FLTP | Double | False |  |
| AlgoBPL | Double | False |  |
| TradeBPL | Double | False |  |
| TotalBPL | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |

## U3_BuySellsAgg

- Columns: 26

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False |  |
| backend | String | False |  |
| ip | String | False |  |
| frontend | String | False |  |
| user | String | False |  |
| Acc | String | False |  |
| Exch | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| NetBook | String | False |  |
| TraderId | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False |  |
| StrikePrice | Float | False |  |
| OptType | String | False |  |
| InstType | String | False |  |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| Expense | Double | False |  |

## U3_conrevNetBookDelta

- Columns: 43

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False | BITMAP |
| backend | String | False | BITMAP |
| ip | String | False | BITMAP |
| frontend | String | False | BITMAP |
| user | String | False | BITMAP |
| Acc | String | False | BITMAP |
| PfNo | Integer | False |  |
| Exch | String | False | BITMAP |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False | BITMAP |
| StrikePrice | Float | False |  |
| OptType | String | False | BITMAP |
| InstType | String | False | BITMAP |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| SellAvg | Double | False |  |
| NetPosition | Long | False |  |
| NetValue | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| FLTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |
| NetBook | String | False | BITMAP |
| RunTs | String | False | BITMAP |
| LegGroupId | String | False | BITMAP |
| LegRole | String | False | BITMAP |
| LegSignal | String | False | BITMAP |
| LegDiff | Double | False |  |
| LegQty | Long | False |  |
| TraderId | Long | False |  |

## U3_NetBook

- Columns: 35

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| sgroup | String | False |  |
| backend | String | False |  |
| ip | String | False |  |
| frontend | String | False |  |
| user | String | False |  |
| Acc | String | False |  |
| Exch | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False |  |
| StrikePrice | Long | False |  |
| OptType | String | False |  |
| InstType | String | False |  |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| FLTP | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |

## U3_NetBookConrev

- Columns: 40

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| NetBook | String | False |  |
| sgroup | String | False |  |
| backend | String | False |  |
| ip | String | False |  |
| frontend | String | False |  |
| user | String | False |  |
| Acc | String | False |  |
| Exch | String | False |  |
| PfNo | Integer | False |  |
| Token | Long | False |  |
| Symbol | String | False |  |
| Expiry | String | False |  |
| StrikePrice | Float | False |  |
| OptType | String | False |  |
| TraderId | Long | False |  |
| InstType | String | False |  |
| BuyQty | Long | False |  |
| BuyValue | Double | False |  |
| SellQty | Long | False |  |
| SellValue | Double | False |  |
| NetQty | Long | False |  |
| NetValue | Double | False |  |
| BuyAvg | Double | False |  |
| SellAvg | Double | False |  |
| NetPrice | Double | False |  |
| LTP | Double | False |  |
| Vega | Double | False |  |
| Theta | Double | False |  |
| Gamma | Double | False |  |
| Delta | Double | False |  |
| Rho | Double | False |  |
| IV | Double | False |  |
| FLTP | Double | False |  |
| AlgoBPL | Double | False |  |
| TradeBPL | Double | False |  |
| TotalBPL | Double | False |  |
| BPL | Double | False |  |
| MTM | Double | False |  |
| MTMF | Double | False |  |
| Expense | Double | False |  |

## VC3_GDBD

- Columns: 10

| Column | Type | Nullable | Index Mode |
|---|---|---|---|
| rundate | String | False |  |
| Symbol | String | False |  |
| GoodDays | Integer | False |  |
| GDP | Double | False |  |
| BadDays | Integer | False |  |
| VeryBadDays | Integer | False |  |
| BDL | Double | False |  |
| LossPer | Double | False |  |
| PriorityScore | Double | False |  |
| PNL | Double | False |  |

