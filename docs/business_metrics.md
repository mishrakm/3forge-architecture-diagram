# Business Metric Candidates

Generated at (UTC): 2026-04-23T06:57:08.306895+00:00

## BuySells

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, BExpense, SExpense, TraderId
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_trade_pnl: SellValue - BuyValue - BExpense - SExpense
- net_position_by_symbol: Aggregate by Symbol, NetBook

## BuySellsAgg

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetPosition, NetValue, NetPrice, BuyAvg, SellAvg, Expense, TraderId
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## BuySellsAggC1

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetPosition, NetValue, NetPrice, BuyAvg, SellAvg, Expense, TraderId, AlgoBPL
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## BuySellsAggC2

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetPosition, NetValue, NetPrice, BuyAvg, SellAvg, Expense, TraderId, AlgoBPL
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## conrevNetBookDelta

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, BuyAvg, SellQty, SellValue, SellAvg, NetPosition, NetValue, NetPrice, LTP, FLTP, Vega, Theta, Gamma, Delta, Rho, IV, BPL, MTM, MTMF, Expense, LegDiff, LegQty, TraderId
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## GroupedPnl

- Numeric columns: Positions, PNL, tt
- pnl_reported: Use existing pnl columns: PNL

## IV_GDBD

- Numeric columns: GoodDays, GDP, BadDays, VeryBadDays, BDL, LossPer, PriorityScore, PNL
- pnl_reported: Use existing pnl columns: PNL

## NetBook

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, BuyAvg, SellQty, SellValue, SellAvg, NetQty, NetValue, NetPrice, LTP, FLTP, Vega, Theta, Gamma, Delta, Rho, IV, BPL, MTM, MTMF, Expense, TraderId
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## NetBookC

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, BuyAvg, SellQty, SellValue, SellAvg, NetQty, NetValue, NetPrice, LTP, FLTP, Vega, Theta, Gamma, Delta, Rho, IV, BPL, MTM, MTMF, Expense, TraderId, AlgoBPL, TradeBPL, TotalBPL
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## NetBookGrouped

- Numeric columns: Positions, PNL, Expense
- pnl_reported: Use existing pnl columns: PNL

## NetBookGroupedFiltered

- Numeric columns: Positions, PNL, tt
- pnl_reported: Use existing pnl columns: PNL

## NetBookSnap

- Numeric columns: snapTime, PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetQty, NetValue, BuyAvg, SellAvg, NetPrice, LTP, Vega, Theta, Gamma, Delta, Rho, IV, FLTP, BPL, MTM, MTMF, Expense, TraderId
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue

## NetBookSnap2

- Numeric columns: snapTime, PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetQty, NetValue, BuyAvg, SellAvg, NetPrice, LTP, Vega, Theta, Gamma, Delta, Rho, IV, FLTP, BPL, MTM, MTMF, Expense
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue

## NetPnl

- Numeric columns: netPNL, tt
- pnl_reported: Use existing pnl columns: netPNL

## SquaredOff

- Numeric columns: PfNo, StrikePrice, NetValue, NetPrice, Expense, TraderId, ConsumableQty, SellQty, SellPrice, SellAvg, SellValue, id, NetPosition, sent, adjusted
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## SquareOff

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetPosition, NetValue, NetPrice, BuyAvg, SellAvg, Expense, TraderId, sent, NetQty, Adjusted, AdjustedQty, id, ts, adjusted, Qty
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## TRADEBOOK

- Numeric columns: UID, AutoNo, PfNo, Token, StrikePrice, OrderType, Price, FillPrice, FillNumber, FillQty, LeavesQty, LastShare, ActualQty, ExchOrderNo, FilledLots, AlgoId, AlgoCategory, TraderId, LTP
- net_position_by_symbol: Aggregate by Symbol, NetBook

## TradeBook

- Numeric columns: UID, AutoNo, PfNo, Token, StrikePrice, OrderType, Price, FillPrice, FillNumber, FillQty, LeavesQty, LastShare, ActualQty, ExchOrderNo, FilledLots, AlgoId, AlgoCategory, TraderId, LTP
- net_position_by_symbol: Aggregate by Symbol, NetBook

## TradeBook_TID

- Numeric columns: UID, AutoNo, PfNo, Token, StrikePrice, OrderType, Price, FillPrice, FillNumber, FillQty, LeavesQty, LastShare, ActualQty, ExchOrderNo, FilledLots, AlgoId, AlgoCategory, TraderId, LTP
- net_position_by_symbol: Aggregate by Symbol, NetBook

## U1_NetBook

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetQty, NetValue, BuyAvg, SellAvg, NetPrice, LTP, Vega, Theta, Gamma, Delta, Rho, IV, FLTP, BPL, MTM, MTMF, Expense
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue

## U2_BuySellsAgg

- Numeric columns: PfNo, Token, TraderId, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetPosition, NetValue, BuyAvg, SellAvg, NetPrice, Expense
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## U2_conrevNetBookDelta

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, BuyAvg, SellQty, SellValue, SellAvg, NetPosition, NetValue, NetPrice, LTP, FLTP, Vega, Theta, Gamma, Delta, Rho, IV, BPL, MTM, MTMF, Expense, LegDiff, LegQty, TraderId
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## U2_NetBook

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetQty, NetValue, BuyAvg, SellAvg, NetPrice, LTP, Vega, Theta, Gamma, Delta, Rho, IV, FLTP, BPL, MTM, MTMF, Expense
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue

## U2_NetBookConrev

- Numeric columns: PfNo, Token, StrikePrice, TraderId, BuyQty, BuyValue, SellQty, SellValue, NetQty, NetValue, BuyAvg, SellAvg, NetPrice, LTP, Vega, Theta, Gamma, Delta, Rho, IV, FLTP, AlgoBPL, TradeBPL, TotalBPL, BPL, MTM, MTMF, Expense
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## U3_BuySellsAgg

- Numeric columns: PfNo, Token, TraderId, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetPosition, NetValue, BuyAvg, SellAvg, NetPrice, Expense
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## U3_conrevNetBookDelta

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, BuyAvg, SellQty, SellValue, SellAvg, NetPosition, NetValue, NetPrice, LTP, FLTP, Vega, Theta, Gamma, Delta, Rho, IV, BPL, MTM, MTMF, Expense, LegDiff, LegQty, TraderId
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## U3_NetBook

- Numeric columns: PfNo, Token, StrikePrice, BuyQty, BuyValue, SellQty, SellValue, NetQty, NetValue, BuyAvg, SellAvg, NetPrice, LTP, Vega, Theta, Gamma, Delta, Rho, IV, FLTP, BPL, MTM, MTMF, Expense
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue

## U3_NetBookConrev

- Numeric columns: PfNo, Token, StrikePrice, TraderId, BuyQty, BuyValue, SellQty, SellValue, NetQty, NetValue, BuyAvg, SellAvg, NetPrice, LTP, Vega, Theta, Gamma, Delta, Rho, IV, FLTP, AlgoBPL, TradeBPL, TotalBPL, BPL, MTM, MTMF, Expense
- turnover_qty: BuyQty + SellQty
- turnover_value: BuyValue + SellValue
- net_position_by_symbol: Aggregate by Symbol, NetBook

## VC3_GDBD

- Numeric columns: GoodDays, GDP, BadDays, VeryBadDays, BDL, LossPer, PriorityScore, PNL
- pnl_reported: Use existing pnl columns: PNL

