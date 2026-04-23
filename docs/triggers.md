# Trigger Flow

Generated at (UTC): 2026-04-23T07:00:03.451392+00:00

Trigger count: 14

## Flow Map

| Trigger | Type | Inputs | Output | Enabled |
|---|---|---|---|---|
| CleanOrders | JOIN | order_msgs_noxml, ResultSet | order_msgs_noxml_clean | True |
| trgBuySells | JOIN | TradeBook_TID, MasterExpenseParams | BuySells | True |
| trgBuySellsAgg | AGGREGATE | BuySells | BuySellsAgg | True |
| trgBuySellsAggC1 | PROJECTION | conrevNetBookDelta, BuySellsAgg | BuySellsAggC1 | True |
| trgBuySellsAggC2 | AGGREGATE | BuySellsAggC1 | BuySellsAggC2 | True |
| trgGroupedPnl | AGGREGATE | NetBookC | GroupedPnl | True |
| trgMergeTraderId | JOIN | TradeBook, MasterTraderIds | TradeBook_TID | True |
| trgNetBook | JOIN | BuySellsAgg, nse_tbt_snap | NetBook | True |
| trgNetBookConRev | JOIN | BuySellsAggC2, nse_tbt_snap | NetBookC | True |
| trgNetBookGrouped | AGGREGATE | NetBookC | NetBookGrouped | True |
| trgNetBookGroupedFiltered | PROJECTION | NetBookGrouped | NetBookGroupedFiltered | True |
| trgNetPnL | AGGREGATE | NetBookGroupedFiltered | NetPnl | True |
| trgTradeBook | JOIN | order_msgs_noxml_clean, ServerUsers | TradeBook | True |
| trgTradeSum | AGGREGATE | TradeBook | TradeSummary | True |

## Trigger Definitions

### CleanOrders

- Type: JOIN
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: order_msgs_noxml, ResultSet
- Output table: order_msgs_noxml_clean

```sql
CREATE TRIGGER CleanOrders OFTYPE JOIN ON order_msgs_noxml,ResultSet,order_msgs_noxml_clean PRIORITY 0 USE type="LEFT" selects="UserIdenti=UserIdenti,Symbol=ResultSet.Symbol,FillNumber=FillNumber,ExchTime=ExchTime,Token=order_msgs_noxml.Token,ProClient=ProClient,Side=Side,ExchOrderNo=ExchOrderNo,PfNo=PfNo,OrderStatus=OrderStatus,HOSTIP=HOSTIP,OrderType=OrderType,FillQty=FillQty,OptType=OptionType,Expiry=ExpiryDate,ActualQty=ActualQty,SystemTime=SystemTime,Acc=Acc,AlgoId=AlgoId,StrikePrice=ResultSet.StrikePrice,ErrorMsg=ErrorMsg,InstType=ResultSet.InstType,Exchange=Exchange,Price=Price,TraderId=TraderId,FillPrice=FillPrice,LeavesQty=LeavesQty,NNF=NNF,LastShare=LastShare" on="order_msgs_noxml.Exchange==ResultSet.Exch && order_msgs_noxml.Token==ResultSet.Token";
```

### trgBuySells

- Type: JOIN
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: TradeBook_TID, MasterExpenseParams
- Output table: BuySells

```sql
CREATE TRIGGER trgBuySells OFTYPE JOIN ON TradeBook_TID,MasterExpenseParams,BuySells PRIORITY 0 USE type="LEFT" selects="sgroup=sgroup,backend=ip,ip=server,frontend=frontend,user=user,Acc=Acc,Exch=Exch,PfNo=0,Token=Token, Symbol=Symbol, Expiry=Expiry,StrikePrice=StrikePrice,OptType=OptType,InstType=TradeBook_TID.InstType,NetBook=NetBook,TraderId=TraderId,BuyQty=(TradeBook_TID.Side==\"BUY\"?FillQty:0),BuyValue=(TradeBook_TID.Side==\"BUY\"?FillQty*FillPrice:0),SellQty=(TradeBook_TID.Side==\"SELL\"?FillQty:0),SellValue=(TradeBook_TID.Side==\"SELL\"?FillQty*FillPrice:0),BExpense=(TradeBook_TID.Side==\"BUY\"?FillQty*FillPrice*ExpPer/100.0:0), SExpense=(TradeBook_TID.Side==\"SELL\"?FillQty*FillPrice*ExpPer/100.0:0)" on="TradeBook_TID.Exch==MasterExpenseParams.Exchange && TradeBook_TID.InstType==MasterExpenseParams.InstType && TradeBook_TID.Side==MasterExpenseParams.Side";
```

### trgBuySellsAgg

- Type: AGGREGATE
- Priority: 1
- Owner: USER
- Enabled: True
- Input tables: BuySells
- Output table: BuySellsAgg

```sql
CREATE TRIGGER trgBuySellsAgg OFTYPE AGGREGATE ON BuySells,BuySellsAgg PRIORITY 1 USE selects="BuyQty=sum(BuyQty), BuyValue=sum(BuyValue), SellQty=sum(SellQty),SellValue=sum(SellValue),NetPosition= sum(BuyQty)-sum(SellQty),NetValue=sum(SellValue)-sum(BuyValue),BuyAvg=sum(BuyQty)>0?sum(BuyValue)/sum(BuyQty):0, SellAvg=sum(SellQty)>0?sum(SellValue)/sum(SellQty):0, NetPrice=(sum(SellValue)-sum(BuyValue))/(sum(SellQty)-sum(BuyQty)), Expense=sum(BExpense)+sum(SExpense)" groupBys="sgroup=sgroup,backend=backend, ip=ip,frontend=frontend, user=user, Acc=Acc, Exch=Exch, PfNo=PfNo,Token=Token, Symbol=Symbol, Expiry=Expiry, StrikePrice=StrikePrice,OptType=OptType,InstType=InstType,TraderId=TraderId,NetBook=NetBook";
```

### trgBuySellsAggC1

- Type: PROJECTION
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: conrevNetBookDelta, BuySellsAgg
- Output table: BuySellsAggC1

```sql
CREATE TRIGGER trgBuySellsAggC1 OFTYPE PROJECTION ON conrevNetBookDelta,BuySellsAgg,BuySellsAggC1 PRIORITY 0 USE selects="sgroup=strTrim(sgroup),backend=strTrim(backend),ip=strTrim(ip),frontend=strTrim(frontend),user=strTrim(user),Acc=strTrim(Acc),Exch=strTrim(Exch),PfNo=PfNo,Token=Token,Symbol=strTrim(Symbol),Expiry=strTrim(Expiry),StrikePrice=StrikePrice,OptType=strTrim(OptType),InstType=strTrim(InstType),BuyQty=BuyQty,BuyValue=BuyValue,SellQty=SellQty,SellValue=SellValue,NetPosition=NetPosition,NetValue=NetValue,NetPrice=NetPrice,BuyAvg=BuyAvg,SellAvg=SellAvg,Expense=Expense,AlgoBPL=(BPL==null?0:BPL),TraderId=TraderId,NetBook=NetBook";
```

### trgBuySellsAggC2

- Type: AGGREGATE
- Priority: 1
- Owner: USER
- Enabled: True
- Input tables: BuySellsAggC1
- Output table: BuySellsAggC2

```sql
CREATE TRIGGER trgBuySellsAggC2 OFTYPE AGGREGATE ON BuySellsAggC1,BuySellsAggC2 PRIORITY 1 USE selects="BuyQty=sum(BuyQty),BuyValue=sum(BuyValue),SellQty=sum(SellQty),SellValue=sum(SellValue),NetPosition=sum(BuyQty)-sum(SellQty),NetValue=sum(SellValue)-sum(BuyValue),BuyAvg=(sum(BuyQty)>0 ? sum(BuyValue)/sum(BuyQty) : 0),SellAvg=(sum(SellQty)>0 ? sum(SellValue)/sum(SellQty) : 0),NetPrice=((sum(SellQty)-sum(BuyQty))!=0         ? (sum(SellValue)-sum(BuyValue))/(sum(SellQty)-sum(BuyQty)): 0),Expense=sum(Expense),AlgoBPL=sum(AlgoBPL)" groupBys="sgroup=sgroup,backend=backend,ip=ip,frontend=frontend,user=user,Acc=Acc,Exch=Exch,PfNo=PfNo,Token=Token,Symbol=Symbol,Expiry=Expiry,StrikePrice=StrikePrice,OptType=OptType,InstType=InstType,TraderId=TraderId,NetBook=NetBook";
```

### trgGroupedPnl

- Type: AGGREGATE
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: NetBookC
- Output table: GroupedPnl

```sql
CREATE TRIGGER trgGroupedPnl OFTYPE AGGREGATE ON NetBookC,GroupedPnl PRIORITY 0 USE selects="Positions=count(NetQty!=0),PNL=sum(BPL+MTM-Expense)" groupBys="sgroup=sgroup";
```

### trgMergeTraderId

- Type: JOIN
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: TradeBook, MasterTraderIds
- Output table: TradeBook_TID

```sql
CREATE TRIGGER trgMergeTraderId OFTYPE JOIN ON TradeBook,MasterTraderIds,TradeBook_TID PRIORITY 0 USE type="LEFT" selects="server=server,user=user,sgroup=sgroup,frontend=frontend,ip=TradeBook.ip,UID=UID,AutoNo=AutoNo,InOutTag=InOutTag,Exch=Exch,PfName=PfName,PfNo=PfNo,Token=Token,InstType=InstType,Symbol=Symbol,Expiry=Expiry,OptType=OptType,StrikePrice=StrikePrice,ProClient=ProClient,Acc=Acc,Side=Side,ExchTimeStamp=ExchTimeStamp,SystemTimeStamp=SystemTimeStamp,OrderType=OrderType,OrderStatus=OrderStatus,Price=Price,FillPrice=FillPrice,FillNumber=FillNumber,FillQty=FillQty,LeavesQty=LeavesQty,OrderNo=OrderNo,LastShare=LastShare,ActualQty=ActualQty,ExchOrderNo=ExchOrderNo,ErrorMsg=ErrorMsg,FilledLots=FilledLots,PAN=PAN,AlgoId=AlgoId,AlgoCategory=AlgoCategory,TradingSymbol=TradingSymbol,NNF=NNF,BrokerId=BrokerId,TraderId=(MasterTraderIds.groupingId==null?TradeBook.TraderId:MasterTraderIds.groupingId),LTP=LTP,NetBook=NetBook" on="TradeBook.ip==MasterTraderIds.backend && TradeBook.TraderId==MasterTraderIds.TraderID";
```

### trgNetBook

- Type: JOIN
- Priority: 2
- Owner: USER
- Enabled: True
- Input tables: BuySellsAgg, nse_tbt_snap
- Output table: NetBook

```sql
CREATE TRIGGER trgNetBook OFTYPE JOIN ON BuySellsAgg,nse_tbt_snap,NetBook PRIORITY 2 USE type="LEFT" selects="netBook=NetBook,sgroup=sgroup,backend=backend,ip=ip,frontend=frontend,user=user,Acc=Acc,Exch=BuySellsAgg.Exch,PfNo=PfNo,Token=BuySellsAgg.Token, Symbol=Symbol, Expiry=Expiry, StrikePrice=StrikePrice,OptType=OptType,TraderId=TraderId, InstType=InstType, BuyQty=BuyQty, BuyValue=BuyValue, SellQty=SellQty,SellValue=SellValue,NetQty= NetPosition, NetValue=NetValue, BuyAvg=BuyAvg, SellAvg=SellAvg, NetPrice=NetPrice, LTP=(LTP/100.0), Vega=gVega*NetPosition, Theta=gTheta*NetPosition, Gamma=gGamma*NetPosition, Delta=gDelta*NetPosition,Rho=gRho*NetPosition, IV=gIV, FLTP=lowerb/100.0, BPL=(BuyQty == SellQty ? SellValue-BuyValue : (BuyQty<SellQty ? (SellAvg-BuyAvg)*minimum(BuyQty,SellQty): (SellAvg-BuyAvg)*minimum(BuyQty,SellQty))), MTM=(BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(LTP/100.0))*(SellQty-BuyQty): ((LTP/100.0)-BuyAvg)*(BuyQty-SellQty))), MTMF=(BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(lowerb/100.0))*(SellQty-BuyQty): ((lowerb/100.0)-BuyAvg)*(BuyQty-SellQty))),Expense=Expense" on="BuySellsAgg.Token==nse_tbt_snap.Token";
```

### trgNetBookConRev

- Type: JOIN
- Priority: 2
- Owner: USER
- Enabled: True
- Input tables: BuySellsAggC2, nse_tbt_snap
- Output table: NetBookC

```sql
CREATE TRIGGER trgNetBookConRev OFTYPE JOIN ON BuySellsAggC2,nse_tbt_snap,NetBookC PRIORITY 2 USE type="LEFT" selects="netBook=NetBook,sgroup=sgroup,backend=backend,ip=ip,frontend=frontend,user=user,Acc=Acc,Exch=BuySellsAggC2.Exch,PfNo=PfNo,Token=BuySellsAggC2.Token,Symbol=Symbol,Expiry=Expiry,StrikePrice=StrikePrice,OptType=OptType,TraderId=TraderId,InstType=InstType,BuyQty=BuyQty,BuyValue=BuyValue,SellQty=SellQty,SellValue=SellValue,NetQty=NetPosition,NetValue=NetValue,BuyAvg=BuyAvg,SellAvg=SellAvg,NetPrice=NetPrice,LTP=(LTP/100.0),Vega=gVega*NetPosition,Theta=gTheta*NetPosition,Gamma=gGamma*NetPosition,Delta=gDelta*NetPosition,Rho=gRho*NetPosition,IV=gIV,FLTP=lowerb/100.0,AlgoBPL=(AlgoBPL==null?0:AlgoBPL),TradeBPL=(BuyQty==SellQty? (SellValue-BuyValue)    : ((SellAvg-BuyAvg)*minimum(BuyQty,SellQty))),TotalBPL=(    (AlgoBPL==null?0:AlgoBPL) +    (        BuyQty==SellQty        ? (SellValue-BuyValue)        : ((SellAvg-BuyAvg)*minimum(BuyQty,SellQty))    )),BPL=(    (AlgoBPL==null?0:AlgoBPL) +    (        BuyQty==SellQty        ? (SellValue-BuyValue)        : ((SellAvg-BuyAvg)*minimum(BuyQty,SellQty))    )),MTM=(    BuyQty==SellQty    ? 0    : (        BuyQty<SellQty        ? (SellAvg-(LTP/100.0))*(SellQty-BuyQty)        : ((LTP/100.0)-BuyAvg)*(BuyQty-SellQty)      )),MTMF=(    BuyQty==SellQty    ? 0    : (        BuyQty<SellQty        ? (SellAvg-(lowerb/100.0))*(SellQty-BuyQty)        : ((lowerb/100.0)-BuyAvg)*(BuyQty-SellQty)      )),Expense=Expense" on="BuySellsAggC2.Token==nse_tbt_snap.Token";
```

### trgNetBookGrouped

- Type: AGGREGATE
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: NetBookC
- Output table: NetBookGrouped

```sql
CREATE TRIGGER trgNetBookGrouped OFTYPE AGGREGATE ON NetBookC,NetBookGrouped PRIORITY 0 USE selects="Positions=count(NetQty!=0),PNL=sum(BPL+MTM-Expense)" groupBys="sgroup=sgroup,backend=backend,ip=ip,frontend=frontend,user=user";
```

### trgNetBookGroupedFiltered

- Type: PROJECTION
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: NetBookGrouped
- Output table: NetBookGroupedFiltered

```sql
CREATE TRIGGER trgNetBookGroupedFiltered OFTYPE PROJECTION ON NetBookGrouped,NetBookGroupedFiltered PRIORITY 0 USE selects="sgroup=sgroup,backend=backend,ip=ip,frontend=frontend,user=user,Positions=Positions,PNL=PNL,tt=1" wheres="sgroup!~\"Z \"";
```

### trgNetPnL

- Type: AGGREGATE
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: NetBookGroupedFiltered
- Output table: NetPnl

```sql
CREATE TRIGGER trgNetPnL OFTYPE AGGREGATE ON NetBookGroupedFiltered,NetPnl PRIORITY 0 USE selects="netPNL=round(sum(PNL))" groupBys="tt=tt";
```

### trgTradeBook

- Type: JOIN
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: order_msgs_noxml_clean, ServerUsers
- Output table: TradeBook

```sql
CREATE TRIGGER trgTradeBook OFTYPE JOIN ON order_msgs_noxml_clean,ServerUsers,TradeBook PRIORITY 0 USE type="LEFT" selects="server=s_name,user=s_user,sgroup=s_groupname,frontend=s_frontend, ip=HOSTIP,AutoNo=1, Exch=Exchange, PfNo=PfNo,Token=Token,InstType=InstType,Symbol=Symbol, Expiry=Expiry, OptType=OptType, StrikePrice=StrikePrice,ProClient=ProClient,Acc=Acc,Side=Side, ExchTimeStamp=ExchTime, SystemTimeStamp=SystemTime, OrderType=OrderType, OrderStatus=OrderStatus, Price=Price, FillPrice=FillPrice, FillNumber=FillNumber, FillQty=FillQty, LeavesQty=LeavesQty, OrderNo=ExchOrderNo,ActualQty=ActualQty, ExchOrderNo=ExchOrderNo, ErrorMsg=ErrorMsg,FilledLots=0, AlgoId=AlgoId, NNF=NNF, TraderId=TraderId, LTP=0,NetBook=NetBook" on="HOSTIP==s_backend";
```

### trgTradeSum

- Type: AGGREGATE
- Priority: 0
- Owner: USER
- Enabled: True
- Input tables: TradeBook
- Output table: TradeSummary

```sql
CREATE TRIGGER trgTradeSum OFTYPE AGGREGATE ON TradeBook,TradeSummary PRIORITY 0 USE selects="buys=sum(Side==\"BUY\"?AutoNo:0), sells=sum(Side==\"SELL\"?AutoNo:0)" groupBys="server=server,user=user,sgroup=sgroup,ip=ip,frontend=frontend";
```

