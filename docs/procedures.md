# Procedures

Generated at (UTC): 2026-04-23T06:57:08.306895+00:00

Procedure count: 22

| Procedure | Type | Return Type | Owner |
|---|---|---|---|
| __ADD_CENTER | __SYSTEM | Object | SYSTEM |
| __ADD_DATASOURCE | __SYSTEM | Object | SYSTEM |
| __ADD_REPLICATION | __SYSTEM | Object | SYSTEM |
| __GET_TIMEZONE | __SYSTEM | Object | SYSTEM |
| __MARK_HISTORICAL_PARTITION_FOR_APPEND | __SYSTEM | Object | SYSTEM |
| __OPTIMIZE_HISTORICAL_TABLE | __SYSTEM | Object | SYSTEM |
| __REMOVE_CENTER | __SYSTEM | Object | SYSTEM |
| __REMOVE_DATASOURCE | __SYSTEM | Object | SYSTEM |
| __REMOVE_REPLICATION | __SYSTEM | Object | SYSTEM |
| __RESET_TIMER_STATS | __SYSTEM | Object | SYSTEM |
| __RESET_TRIGGER_STATS | __SYSTEM | Object | SYSTEM |
| __SCHEDULE_TIMER | __SYSTEM | Object | SYSTEM |
| __SET_TIMEZONE | __SYSTEM | Object | SYSTEM |
| __SHOW_TIMER_ERROR | __SYSTEM | Object | SYSTEM |
| __SHOW_TRIGGER_ERROR | __SYSTEM | Object | SYSTEM |
| cumGDBD | AMISCRIPT | String | USER |
| cumGDBDiv | AMISCRIPT | String | USER |
| netBook | AMISCRIPT | String | USER |
| netBook2 | AMISCRIPT | String | USER |
| NetBookConrevPositions | AMISCRIPT | String | USER |
| NetBookMergeConrev | AMISCRIPT | String | USER |
| netBookSnap | AMISCRIPT | String | USER |

## Procedure Definitions

### __ADD_CENTER

- Type: __SYSTEM
- Return type: Object
- Arguments: CenterName String nonull,Url String nonull,CertFile String,Passw
- Owner: SYSTEM

```sql
CREATE PROCEDURE __ADD_CENTER OFTYPE __SYSTEM;
```

### __ADD_DATASOURCE

- Type: __SYSTEM
- Return type: Object
- Arguments: Name String nonull,DatasourceType String nonull,URL String nonul
- Owner: SYSTEM

```sql
CREATE PROCEDURE __ADD_DATASOURCE OFTYPE __SYSTEM;
```

### __ADD_REPLICATION

- Type: __SYSTEM
- Return type: Object
- Arguments: Definition String nonull,Name String,Mapping String,Options Stri
- Owner: SYSTEM

```sql
CREATE PROCEDURE __ADD_REPLICATION OFTYPE __SYSTEM;
```

### __GET_TIMEZONE

- Type: __SYSTEM
- Return type: Object
- Arguments: 
- Owner: SYSTEM

```sql
CREATE PROCEDURE __GET_TIMEZONE OFTYPE __SYSTEM;
```

### __MARK_HISTORICAL_PARTITION_FOR_APPEND

- Type: __SYSTEM
- Return type: Object
- Arguments: TableName String nonull,PartitionID Integer nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __MARK_HISTORICAL_PARTITION_FOR_APPEND OFTYPE __SYSTEM;
```

### __OPTIMIZE_HISTORICAL_TABLE

- Type: __SYSTEM
- Return type: Object
- Arguments: TableName String nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __OPTIMIZE_HISTORICAL_TABLE OFTYPE __SYSTEM;
```

### __REMOVE_CENTER

- Type: __SYSTEM
- Return type: Object
- Arguments: Name String nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __REMOVE_CENTER OFTYPE __SYSTEM;
```

### __REMOVE_DATASOURCE

- Type: __SYSTEM
- Return type: Object
- Arguments: Name String nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __REMOVE_DATASOURCE OFTYPE __SYSTEM;
```

### __REMOVE_REPLICATION

- Type: __SYSTEM
- Return type: Object
- Arguments: Name String nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __REMOVE_REPLICATION OFTYPE __SYSTEM;
```

### __RESET_TIMER_STATS

- Type: __SYSTEM
- Return type: Object
- Arguments: TimerName String nonull,ExecutedStats boolean nonull,ErrorStats 
- Owner: SYSTEM

```sql
CREATE PROCEDURE __RESET_TIMER_STATS OFTYPE __SYSTEM;
```

### __RESET_TRIGGER_STATS

- Type: __SYSTEM
- Return type: Object
- Arguments: TriggerName String nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __RESET_TRIGGER_STATS OFTYPE __SYSTEM;
```

### __SCHEDULE_TIMER

- Type: __SYSTEM
- Return type: Object
- Arguments: TimerName String nonull,DelayMillis long nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __SCHEDULE_TIMER OFTYPE __SYSTEM;
```

### __SET_TIMEZONE

- Type: __SYSTEM
- Return type: Object
- Arguments: timezone String nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __SET_TIMEZONE OFTYPE __SYSTEM;
```

### __SHOW_TIMER_ERROR

- Type: __SYSTEM
- Return type: Object
- Arguments: TimerName String nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __SHOW_TIMER_ERROR OFTYPE __SYSTEM;
```

### __SHOW_TRIGGER_ERROR

- Type: __SYSTEM
- Return type: Object
- Arguments: TriggerName String nonull
- Owner: SYSTEM

```sql
CREATE PROCEDURE __SHOW_TRIGGER_ERROR OFTYPE __SYSTEM;
```

### cumGDBD

- Type: AMISCRIPT
- Return type: String
- Arguments: user String,startdt String,enddt String
- Owner: USER

```sql
CREATE PROCEDURE cumGDBD OFTYPE AMISCRIPT USE logging="VERBOSE" script="\nDROP TABLE IF EXISTS ${user}_TradeBook;\nCREATE PUBLIC TABLE ${user}_TradeBook(server String BITMAP,user String BITMAP,sgroup String BITMAP,frontend String BITMAP,ip String BITMAP,UID Long,AutoNo Long,InOutTag String BITMAP,Exch String BITMAP,PfName String BITMAP,PfNo Integer,Token Long,InstType String BITMAP,Symbol String BITMAP,Expiry String BITMAP,OptType String BITMAP,StrikePrice Long,ProClient String BITMAP,Acc String BITMAP,Side String BITMAP,ExchTimeStamp String,SystemTimeStamp String,OrderType Long,OrderStatus String BITMAP,Price Double,FillPrice Double,FillNumber Long,FillQty Long,LeavesQty Long,OrderNo String,LastShare Long,ActualQty Long,ExchOrderNo Long,ErrorMsg String,FilledLots Long,PAN String BITMAP,AlgoId Long,AlgoCategory Long,TradingSymbol String BITMAP,NNF String,BrokerId String,TraderId Long,LTP Double) USE NoBroadcast;\n\ninsert into ${user}_TradeBook FROM select server,user,sgroup,frontend,ip,UID,AutoNo,InOutTag,Exch, PfName, PfNo, Token, InstType, strTrim(Symbol) as Symbol, Expiry, OptType, StrikePrice, ProClient, Acc, Side, strCut(ExchTimeStamp,\" \",\"0\") as ExchTimeStamp, SystemTimeStamp, OrderType, OrderStatus, Price, FillPrice, FillNumber, FillQty, LeavesQty, OrderNo, LastShare, ActualQty, ExchOrderNo, ErrorMsg, FilledLots, PAN, AlgoId, AlgoCategory, TradingSymbol, NNF, BrokerId, TraderId,LTP from TRADEBOOK where Date>=\"${startdt}\" && Date<=\"${enddt}\" && (sgroup==\"STOCKS 1 CALL\" || sgroup==\"STOCKS 2 PUT\" || sgroup==\"CONREV VC3\");\n\nDROP TABLE IF EXISTS ${user}_BuySell;\nCREATE TABLE ${user}_BuySell as SELECT ExchTimeStamp, sgroup,ip as backend,server as ip,frontend,user,Acc,Exch,0 as PfNo,Token,Symbol,Expiry,StrikePrice,OptType,${user}_TradeBook.InstType as InstType,(${user}_TradeBook.Side==\"BUY\"?FillQty:0) as BuyQty,(${user}_TradeBook.Side==\"BUY\"?FillQty*FillPrice:0) as BuyValue,(${user}_TradeBook.Side==\"SELL\"?FillQty:0) as SellQty,(${user}_TradeBook.Side==\"SELL\"?FillQty*FillPrice:0) as SellValue,(${user}_TradeBook.Side==\"BUY\"?FillQty*FillPrice*ExpPer/100.0:0) as BExpense,(${user}_TradeBook.Side==\"SELL\"?FillQty*FillPrice*ExpPer/100.0:0) as SExpense from ${user}_TradeBook LEFT JOIN MasterExpenseParams ON ${user}_TradeBook.Exch==MasterExpenseParams.Exchange && ${user}_TradeBook.InstType==MasterExpenseParams.InstType && ${user}_TradeBook.Side==MasterExpenseParams.Side;\n\nDROP TABLE IF EXISTS ${user}_BuySellsAgg;\nCREATE TABLE ${user}_BuySellsAgg as select ExchTimeStamp, sgroup,backend, ip,frontend,user, Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType,sum(BuyQty) as BuyQty,sum(BuyValue) as BuyValue,sum(SellQty) as SellQty,sum(SellValue) as SellValue, sum(BuyQty)-sum(SellQty) as NetPosition,sum(SellValue)-sum(BuyValue) as NetValue,sum(BuyQty)>0?sum(BuyValue)/sum(BuyQty):0 as BuyAvg, sum(SellQty)>0?sum(SellValue)/sum(SellQty):0 as SellAvg, (sum(SellValue)-sum(BuyValue))/(sum(SellQty)-sum(BuyQty)) as NetPrice, sum(BExpense)+sum(SExpense) as Expense from ${user}_BuySell group by ExchTimeStamp, sgroup,backend, ip,frontend,user, Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType;\n\nDROP TABLE IF EXISTS ${user}_NetBook;\nCREATE TABLE ${user}_NetBook as select ExchTimeStamp, sgroup,backend,ip,frontend,user,Acc,${user}_BuySellsAgg.Exch as Exch,PfNo,${user}_BuySellsAgg.Token as Token, Symbol, Expiry, StrikePrice,OptType, InstType, BuyQty, BuyValue, SellQty,SellValue,NetPosition as NetQty, NetValue, BuyAvg, SellAvg, NetPrice, (LTP/100.0) as LTP, gVega*NetPosition as Vega, gTheta*NetPosition as Theta, gGamma*NetPosition as Gamma, gDelta*NetPosition as Delta,gRho*NetPosition as Rho, gIV as IV, lowerb/100.0 as FLTP, (BuyQty == SellQty ? SellValue-BuyValue : (BuyQty<SellQty ? (SellAvg-BuyAvg)*minimum(BuyQty,SellQty): (SellAvg-BuyAvg)*minimum(BuyQty,SellQty))) as BPL, (BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(LTP/100.0))*(SellQty-BuyQty): ((LTP/100.0)-BuyAvg)*(BuyQty-SellQty))) as MTM, (BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(lowerb/100.0))*(SellQty-BuyQty): ((lowerb/100.0)-BuyAvg)*(BuyQty-SellQty))) as MTMF,Expense from ${user}_BuySellsAgg LEFT JOIN  nse_tbt_snap  on ${user}_BuySellsAgg.Token==nse_tbt_snap.Token;\n\nDROP TABLE IF EXISTS ${user}_NetValues;\nCREATE TABLE ${user}_NetValues as select ExchTimeStamp,strTrim(Symbol) as Symbol,sum(NetValue) as NetValue, 0 as GoodDay,0.0 as GDP,0 as BadDay,0.0 as BDL,0 as VeryBadDay,0.00 as VBDL from ${user}_NetBook where NetQty==0 group by ExchTimeStamp,strTrim(Symbol);\n\nupdate ${user}_NetValues set GoodDay=1,GDP=NetValue where NetValue>0;\nupdate ${user}_NetValues set BadDay=1,BDL=NetValue where NetValue<=0 and NetValue>-25000;\nupdate ${user}_NetValues set VeryBadDay=1,VBDL=NetValue where NetValue<=-25000;\n\ndouble max_pnl=select max(NetValue) from ${user}_NetValues;\ndouble min_pnl=select min(NetValue) from ${user}_NetValues;\n\nDROP TABLE IF EXISTS ${user}_GDBD;\nCREATE PUBLIC TABLE ${user}_GDBD as select formatDate(timestamp(),\"YYYYMMdd\",\"IST\") as rundate,Symbol,sum(GoodDay) as GoodDays,sum(GDP) as GDP,sum(BadDay) as BadDays,sum(VeryBadDay) as VeryBadDays,sum(BDL+VBDL) as BDL,0.0 as LossPer,0.00 as PriorityScore,sum(GDP+BDL+VBDL) as PNL from ${user}_NetValues group by Symbol;\nupdate ${user}_GDBD  set LossPer=-1 where GoodDays==0;\nupdate ${user}_GDBD set LossPer=BDL*-100/GDP where GoodDays>0;\nupdate ${user}_GDBD set PriorityScore=LossPer*(power(VeryBadDays,2)+BadDays+1)/(GoodDays+1);\n\n\nDROP TABLE IF EXISTS ${user}_BuySell;\nDROP TABLE IF EXISTS ${user}_BuySellsAgg;\nDROP TABLE IF EXISTS ${user}_TradeBook;\nDROP TABLE IF EXISTS ${user}_NetBook;\nDROP TABLE IF EXISTS ${user}_NetValues;\n//DROP TABLE IF EXISTS ${user}_GDBD;\n" arguments="string user, string startdt, string enddt";
```

### cumGDBDiv

- Type: AMISCRIPT
- Return type: String
- Arguments: user String,startdt String,enddt String
- Owner: USER

```sql
CREATE PROCEDURE cumGDBDiv OFTYPE AMISCRIPT USE logging="VERBOSE" script="\nDROP TABLE IF EXISTS ${user}_TradeBook;\nCREATE PUBLIC TABLE ${user}_TradeBook(server String BITMAP,user String BITMAP,sgroup String BITMAP,frontend String BITMAP,ip String BITMAP,UID Long,AutoNo Long,InOutTag String BITMAP,Exch String BITMAP,PfName String BITMAP,PfNo Integer,Token Long,InstType String BITMAP,Symbol String BITMAP,Expiry String BITMAP,OptType String BITMAP,StrikePrice Long,ProClient String BITMAP,Acc String BITMAP,Side String BITMAP,ExchTimeStamp String,SystemTimeStamp String,OrderType Long,OrderStatus String BITMAP,Price Double,FillPrice Double,FillNumber Long,FillQty Long,LeavesQty Long,OrderNo String,LastShare Long,ActualQty Long,ExchOrderNo Long,ErrorMsg String,FilledLots Long,PAN String BITMAP,AlgoId Long,AlgoCategory Long,TradingSymbol String BITMAP,NNF String,BrokerId String,TraderId Long,LTP Double) USE NoBroadcast;\n\ninsert into ${user}_TradeBook FROM select server,user,sgroup,frontend,ip,UID,AutoNo,InOutTag,Exch, PfName, PfNo, Token, InstType, strTrim(Symbol) as Symbol, Expiry, OptType, StrikePrice, ProClient, Acc, Side, strCut(ExchTimeStamp,\" \",\"0\") as ExchTimeStamp, SystemTimeStamp, OrderType, OrderStatus, Price, FillPrice, FillNumber, FillQty, LeavesQty, OrderNo, LastShare, ActualQty, ExchOrderNo, ErrorMsg, FilledLots, PAN, AlgoId, AlgoCategory, TradingSymbol, NNF, BrokerId, TraderId,LTP from TRADEBOOK where Date>=\"${startdt}\" && Date<=\"${enddt}\" && (sgroup==\"PC1B\" || sgroup==\"PC1S\" || sgroup==\"PC2\");\n\nDROP TABLE IF EXISTS ${user}_BuySell;\nCREATE TABLE ${user}_BuySell as SELECT ExchTimeStamp, sgroup,ip as backend,server as ip,frontend,user,Acc,Exch,0 as PfNo,Token,Symbol,Expiry,StrikePrice,OptType,${user}_TradeBook.InstType as InstType,(${user}_TradeBook.Side==\"BUY\"?FillQty:0) as BuyQty,(${user}_TradeBook.Side==\"BUY\"?FillQty*FillPrice:0) as BuyValue,(${user}_TradeBook.Side==\"SELL\"?FillQty:0) as SellQty,(${user}_TradeBook.Side==\"SELL\"?FillQty*FillPrice:0) as SellValue,(${user}_TradeBook.Side==\"BUY\"?FillQty*FillPrice*ExpPer/100.0:0) as BExpense,(${user}_TradeBook.Side==\"SELL\"?FillQty*FillPrice*ExpPer/100.0:0) as SExpense from ${user}_TradeBook LEFT JOIN MasterExpenseParams ON ${user}_TradeBook.Exch==MasterExpenseParams.Exchange && ${user}_TradeBook.InstType==MasterExpenseParams.InstType && ${user}_TradeBook.Side==MasterExpenseParams.Side;\n\nDROP TABLE IF EXISTS ${user}_BuySellsAgg;\nCREATE TABLE ${user}_BuySellsAgg as select ExchTimeStamp, sgroup,backend, ip,frontend,user, Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType,sum(BuyQty) as BuyQty,sum(BuyValue) as BuyValue,sum(SellQty) as SellQty,sum(SellValue) as SellValue, sum(BuyQty)-sum(SellQty) as NetPosition,sum(SellValue)-sum(BuyValue) as NetValue,sum(BuyQty)>0?sum(BuyValue)/sum(BuyQty):0 as BuyAvg, sum(SellQty)>0?sum(SellValue)/sum(SellQty):0 as SellAvg, (sum(SellValue)-sum(BuyValue))/(sum(SellQty)-sum(BuyQty)) as NetPrice, sum(BExpense)+sum(SExpense) as Expense from ${user}_BuySell group by ExchTimeStamp, sgroup,backend, ip,frontend,user, Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType;\n\nDROP TABLE IF EXISTS ${user}_NetBook;\nCREATE TABLE ${user}_NetBook as select ExchTimeStamp, sgroup,backend,ip,frontend,user,Acc,${user}_BuySellsAgg.Exch as Exch,PfNo,${user}_BuySellsAgg.Token as Token, Symbol, Expiry, StrikePrice,OptType, InstType, BuyQty, BuyValue, SellQty,SellValue,NetPosition as NetQty, NetValue, BuyAvg, SellAvg, NetPrice, (LTP/100.0) as LTP, gVega*NetPosition as Vega, gTheta*NetPosition as Theta, gGamma*NetPosition as Gamma, gDelta*NetPosition as Delta,gRho*NetPosition as Rho, gIV as IV, lowerb/100.0 as FLTP, (BuyQty == SellQty ? SellValue-BuyValue : (BuyQty<SellQty ? (SellAvg-BuyAvg)*minimum(BuyQty,SellQty): (SellAvg-BuyAvg)*minimum(BuyQty,SellQty))) as BPL, (BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(LTP/100.0))*(SellQty-BuyQty): ((LTP/100.0)-BuyAvg)*(BuyQty-SellQty))) as MTM, (BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(lowerb/100.0))*(SellQty-BuyQty): ((lowerb/100.0)-BuyAvg)*(BuyQty-SellQty))) as MTMF,Expense from ${user}_BuySellsAgg LEFT JOIN  nse_tbt_snap  on ${user}_BuySellsAgg.Token==nse_tbt_snap.Token;\n\nDROP TABLE IF EXISTS ${user}_NetValues;\nCREATE TABLE ${user}_NetValues as select ExchTimeStamp,strTrim(Symbol) as Symbol,sum(NetValue) as NetValue, 0 as GoodDay,0.0 as GDP,0 as BadDay,0.0 as BDL,0 as VeryBadDay,0.00 as VBDL from ${user}_NetBook where NetQty==0 group by ExchTimeStamp,strTrim(Symbol);\n\nupdate ${user}_NetValues set GoodDay=1,GDP=NetValue where NetValue>0;\nupdate ${user}_NetValues set BadDay=1,BDL=NetValue where NetValue<=0 and NetValue>-25000;\nupdate ${user}_NetValues set VeryBadDay=1,VBDL=NetValue where NetValue<=-25000;\n\ndouble max_pnl=select max(NetValue) from ${user}_NetValues;\ndouble min_pnl=select min(NetValue) from ${user}_NetValues;\n\nDROP TABLE IF EXISTS ${user}_GDBD;\nCREATE PUBLIC TABLE ${user}_GDBD as select formatDate(timestamp(),\"YYYYMMdd\",\"IST\") as rundate,Symbol,sum(GoodDay) as GoodDays,sum(GDP) as GDP,sum(BadDay) as BadDays,sum(VeryBadDay) as VeryBadDays,sum(BDL+VBDL) as BDL,0.0 as LossPer,0.00 as PriorityScore,sum(GDP+BDL+VBDL) as PNL from ${user}_NetValues group by Symbol;\nupdate ${user}_GDBD  set LossPer=-1 where GoodDays==0;\nupdate ${user}_GDBD set LossPer=BDL*-100/GDP where GoodDays>0;\nupdate ${user}_GDBD set PriorityScore=LossPer*(power(VeryBadDays,2)+BadDays+1)/(GoodDays+1);\n\n\nDROP TABLE IF EXISTS ${user}_BuySell;\nDROP TABLE IF EXISTS ${user}_BuySellsAgg;\nDROP TABLE IF EXISTS ${user}_TradeBook;\nDROP TABLE IF EXISTS ${user}_NetBook;\nDROP TABLE IF EXISTS ${user}_NetValues;\n//DROP TABLE IF EXISTS ${user}_GDBD;\n" arguments="string user, string startdt, string enddt";
```

### netBook

- Type: AMISCRIPT
- Return type: String
- Arguments: user String,starttime long,endtime long
- Owner: USER

```sql
CREATE PROCEDURE netBook OFTYPE AMISCRIPT USE logging="verbose" script="\n\nlong startdt=formatDate(starttime,\"yyyyMMdd\",\"IST\");\nlong enddt=formatDate(endtime,\"yyyyMMdd\",\"IST\");\nlong today=formatDate(timestamp(),\"yyyyMMdd\",\"IST\");\n\ndrop table IF EXISTS ${user}_TradeBook;\nCREATE PUBLIC TABLE ${user}_TradeBook(server String BITMAP,user String BITMAP,sgroup String BITMAP,frontend String BITMAP,ip String BITMAP,UID Long,AutoNo Long,InOutTag String BITMAP,Exch String BITMAP,PfName String BITMAP,PfNo Integer,Token Long,InstType String BITMAP,Symbol String BITMAP,Expiry String BITMAP,OptType String BITMAP,StrikePrice Long,ProClient String BITMAP,Acc String BITMAP,Side String BITMAP,ExchTimeStamp String,SystemTimeStamp String,OrderType Long,OrderStatus String BITMAP,Price Double,FillPrice Double,FillNumber Long,FillQty Long,LeavesQty Long,OrderNo String,LastShare Long,ActualQty Long,ExchOrderNo Long,ErrorMsg String,FilledLots Long,PAN String BITMAP,AlgoId Long,AlgoCategory Long,TradingSymbol String BITMAP,NNF String,BrokerId String,TraderId Long,LTP Double) USE NoBroadcast;\n\nif(startdt==today || enddt==today) {\n    insert into ${user}_TradeBook FROM select server,user,sgroup,frontend,ip,UID,AutoNo,InOutTag,Exch, PfName, PfNo, Token, InstType, Symbol, Expiry, OptType, StrikePrice, ProClient, Acc, Side, ExchTimeStamp, SystemTimeStamp, OrderType, OrderStatus, Price, FillPrice, FillNumber, FillQty, LeavesQty, OrderNo, LastShare, ActualQty, ExchOrderNo, ErrorMsg, FilledLots, PAN, AlgoId, AlgoCategory, TradingSymbol, NNF, BrokerId, TraderId,LTP from TradeBook where parseDate(ExchTimeStamp,\"yyyy-MM-dd HH:mm:ss\",\"IST\")>=${starttime} && parseDate(ExchTimeStamp,\"yyyy-MM-dd HH:mm:ss\",\"IST\")<=${endtime} ;\n}\n\nif(startdt!=today || enddt!=today) {\n    string tablname =\"TRADEBOOK\";\n    insert into ${user}_TradeBook FROM select server,user,sgroup,frontend,ip,UID,AutoNo,InOutTag,Exch, PfName, PfNo, Token, InstType, Symbol, Expiry, OptType, StrikePrice, ProClient, Acc, Side, ExchTimeStamp, SystemTimeStamp, OrderType, OrderStatus, Price, FillPrice, FillNumber, FillQty, LeavesQty, OrderNo, LastShare, ActualQty, ExchOrderNo, ErrorMsg, FilledLots, PAN, AlgoId, AlgoCategory, TradingSymbol, NNF, BrokerId, TraderId,LTP from  ${tablname} where parseDate(ExchTimeStamp,\"yyyy-MM-dd HH:mm:ss\",\"IST\")>=${starttime} && parseDate(ExchTimeStamp,\"yyyy-MM-dd HH:mm:ss\",\"IST\")<=${endtime} && ip!=\"1.1.1.1\";\n}\n\ndrop table IF EXISTS ${user}_BuySell;\ncreate public table ${user}_BuySell as SELECT sgroup,ip as backend,server as ip,frontend,user,Acc,Exch,0 as PfNo,Token,Symbol,Expiry,StrikePrice,OptType,${user}_TradeBook.InstType as InstType,(${user}_TradeBook.Side==\"BUY\"?FillQty:0) as BuyQty,(${user}_TradeBook.Side==\"BUY\"?FillQty*FillPrice:0) as BuyValue,(${user}_TradeBook.Side==\"SELL\"?FillQty:0) as SellQty,(${user}_TradeBook.Side==\"SELL\"?FillQty*FillPrice:0) as SellValue,(${user}_TradeBook.Side==\"BUY\"?FillQty*FillPrice*ExpPer/100.0:0) as BExpense,(${user}_TradeBook.Side==\"SELL\"?FillQty*FillPrice*ExpPer/100.0:0) as SExpense from ${user}_TradeBook LEFT JOIN MasterExpenseParams ON ${user}_TradeBook.Exch==MasterExpenseParams.Exchange && ${user}_TradeBook.InstType==MasterExpenseParams.InstType && ${user}_TradeBook.Side==MasterExpenseParams.Side && user~~\"${user}\";\n\ndrop table IF EXISTS ${user}_BuySellsAgg;\ncreate public table ${user}_BuySellsAgg as select sgroup,backend, ip,frontend,user, Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType,sum(BuyQty) as BuyQty,sum(BuyValue) as BuyValue,sum(SellQty) as SellQty,sum(SellValue) as SellValue, sum(BuyQty)-sum(SellQty) as NetPosition,sum(SellValue)-sum(BuyValue) as NetValue,sum(BuyQty)>0?sum(BuyValue)/sum(BuyQty):0 as BuyAvg, sum(SellQty)>0?sum(SellValue)/sum(SellQty):0 as SellAvg, (sum(SellValue)-sum(BuyValue))/(sum(SellQty)-sum(BuyQty)) as NetPrice, sum(BExpense)+sum(SExpense) as Expense from ${user}_BuySell group by sgroup,backend, ip,frontend,user, Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType;\n\ndrop table IF EXISTS ${user}_NetBook;\ncreate public table ${user}_NetBook as select sgroup,backend,ip,frontend,user,Acc,${user}_BuySellsAgg.Exch as Exch,PfNo,${user}_BuySellsAgg.Token as Token, Symbol, Expiry, StrikePrice,OptType, InstType, BuyQty, BuyValue, SellQty,SellValue,NetPosition as NetQty, NetValue, BuyAvg, SellAvg, NetPrice, (LTP/100.0) as LTP, gVega*NetPosition as Vega, gTheta*NetPosition as Theta, gGamma*NetPosition as Gamma, gDelta*NetPosition as Delta,gRho*NetPosition as Rho, gIV as IV, lowerb/100.0 as FLTP, (BuyQty == SellQty ? SellValue-BuyValue : (BuyQty<SellQty ? (SellAvg-BuyAvg)*minimum(BuyQty,SellQty): (SellAvg-BuyAvg)*minimum(BuyQty,SellQty))) as BPL, (BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(LTP/100.0))*(SellQty-BuyQty): ((LTP/100.0)-BuyAvg)*(BuyQty-SellQty))) as MTM, (BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(lowerb/100.0))*(SellQty-BuyQty): ((lowerb/100.0)-BuyAvg)*(BuyQty-SellQty))) as MTMF,Expense from ${user}_BuySellsAgg LEFT JOIN  nse_tbt_snap  on ${user}_BuySellsAgg.Token==nse_tbt_snap.Token;\n\ndrop table IF EXISTS ${user}_BuySell;\ndrop table IF EXISTS ${user}_BuySellsAgg;\ndrop table IF EXISTS ${user}_TradeBook;\n\n" arguments="string user, long starttime, long endtime";
```

### netBook2

- Type: AMISCRIPT
- Return type: String
- Arguments: user String,starttime long,endtime long
- Owner: USER

```sql
CREATE PROCEDURE netBook2 OFTYPE AMISCRIPT USE logging="verbose" script="\n\nlong startdt=formatDate(starttime,\"yyyyMMdd\",\"IST\");\nlong enddt=formatDate(endtime,\"yyyyMMdd\",\"IST\");\nlong today=formatDate(timestamp(),\"yyyyMMdd\",\"IST\");\n\ndrop table IF EXISTS ${user}_TradeBook;\nCREATE PUBLIC TABLE ${user}_TradeBook(server String BITMAP,user String BITMAP,sgroup String BITMAP,frontend String BITMAP,ip String BITMAP,UID Long,AutoNo Long,InOutTag String BITMAP,Exch String BITMAP,PfName String BITMAP,PfNo Integer,Token Long,InstType String BITMAP,Symbol String BITMAP,Expiry String BITMAP,OptType String BITMAP,StrikePrice Long,ProClient String BITMAP,Acc String BITMAP,Side String BITMAP,ExchTimeStamp String,SystemTimeStamp String,OrderType Long,OrderStatus String BITMAP,Price Double,FillPrice Double,FillNumber Long,FillQty Long,LeavesQty Long,OrderNo String,LastShare Long,ActualQty Long,ExchOrderNo Long,ErrorMsg String,FilledLots Long,PAN String BITMAP,AlgoId Long,AlgoCategory Long,TradingSymbol String BITMAP,NNF String,BrokerId String,TraderId Long,LTP Double) USE NoBroadcast;\n\nif(startdt==today || enddt==today) {\n  insert into ${user}_TradeBook FROM select server,user,sgroup,frontend,ip,UID,AutoNo,InOutTag,Exch, PfName, PfNo, Token, InstType, Symbol, Expiry, OptType, StrikePrice, ProClient, Acc, Side, ExchTimeStamp, SystemTimeStamp, OrderType, OrderStatus, Price, FillPrice, FillNumber, FillQty, LeavesQty, OrderNo, LastShare, ActualQty, ExchOrderNo, ErrorMsg, FilledLots, PAN, AlgoId, AlgoCategory, TradingSymbol, NNF, BrokerId, TraderId,LTP from TradeBook where parseDate(ExchTimeStamp,\"yyyy-MM-dd HH:mm:ss\",\"IST\")>=${starttime} && parseDate(ExchTimeStamp,\"yyyy-MM-dd HH:mm:ss\",\"IST\")<=${endtime};\n} \n\nif(startdt!=today || enddt!=today) {\n  string tablname =\"TRADEBOOK\";\n  insert into ${user}_TradeBook FROM select server,user,sgroup,frontend,ip,UID,AutoNo,InOutTag,Exch, PfName, PfNo, Token, InstType, Symbol, Expiry, OptType, StrikePrice, ProClient, Acc, Side, ExchTimeStamp, SystemTimeStamp, OrderType, OrderStatus, Price, FillPrice, FillNumber, FillQty, LeavesQty, OrderNo, LastShare, ActualQty, ExchOrderNo, ErrorMsg, FilledLots, PAN, AlgoId, AlgoCategory, TradingSymbol, NNF, BrokerId, TraderId,LTP from  ${tablname} where parseDate(ExchTimeStamp,\"yyyy-MM-dd HH:mm:ss\",\"IST\")>=${starttime} && parseDate(ExchTimeStamp,\"yyyy-MM-dd HH:mm:ss\",\"IST\")<=${endtime};\n\n}\n\ndrop table IF EXISTS ${user}_BuySell;\ncreate public table ${user}_BuySell as SELECT sgroup,ip as backend,server as ip,frontend,user,Acc,Exch,0 as PfNo,Token,Symbol,Expiry,StrikePrice,OptType,${user}_TradeBook.InstType as InstType,(${user}_TradeBook.Side==\"BUY\"?FillQty:0) as BuyQty,(${user}_TradeBook.Side==\"BUY\"?FillQty*FillPrice:0) as BuyValue,(${user}_TradeBook.Side==\"SELL\"?FillQty:0) as SellQty,(${user}_TradeBook.Side==\"SELL\"?FillQty*FillPrice:0) as SellValue,(${user}_TradeBook.Side==\"BUY\"?FillQty*FillPrice*ExpPer/100.0:0) as BExpense,(${user}_TradeBook.Side==\"SELL\"?FillQty*FillPrice*ExpPer/100.0:0) as SExpense from ${user}_TradeBook LEFT JOIN MasterExpenseParams ON ${user}_TradeBook.Exch==MasterExpenseParams.Exchange && ${user}_TradeBook.InstType==MasterExpenseParams.InstType && ${user}_TradeBook.Side==MasterExpenseParams.Side && user~~\"${user}\";\n\ndrop table IF EXISTS ${user}_BuySellsAgg;\ncreate public table ${user}_BuySellsAgg as select sgroup,backend, ip,frontend,user, Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType,sum(BuyQty) as BuyQty,sum(BuyValue) as BuyValue,sum(SellQty) as SellQty,sum(SellValue) as SellValue, sum(BuyQty)-sum(SellQty) as NetPosition,sum(SellValue)-sum(BuyValue) as NetValue,sum(BuyQty)>0?sum(BuyValue)/sum(BuyQty):0 as BuyAvg, sum(SellQty)>0?sum(SellValue)/sum(SellQty):0 as SellAvg, (sum(SellValue)-sum(BuyValue))/(sum(SellQty)-sum(BuyQty)) as NetPrice, sum(BExpense)+sum(SExpense) as Expense from ${user}_BuySell group by sgroup,backend, ip,frontend,user, Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType;\n\ndrop table IF EXISTS ${user}_NetBook;\ncreate public table ${user}_NetBook as select sgroup,backend,ip,frontend,user,Acc,${user}_BuySellsAgg.Exch as Exch,PfNo,${user}_BuySellsAgg.Token as Token, Symbol, Expiry, StrikePrice,OptType, InstType, BuyQty, BuyValue, SellQty,SellValue,NetPosition as NetQty, NetValue, BuyAvg, SellAvg, NetPrice, (LTP/100.0) as LTP, gVega*NetPosition as Vega, gTheta*NetPosition as Theta, gGamma*NetPosition as Gamma, gDelta*NetPosition as Delta,gRho*NetPosition as Rho, gIV as IV, lowerb/100.0 as FLTP, (BuyQty == SellQty ? SellValue-BuyValue : (BuyQty<SellQty ? (SellAvg-BuyAvg)*minimum(BuyQty,SellQty): (SellAvg-BuyAvg)*minimum(BuyQty,SellQty))) as BPL, (BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(LTP/100.0))*(SellQty-BuyQty): ((LTP/100.0)-BuyAvg)*(BuyQty-SellQty))) as MTM, (BuyQty == SellQty ? 0 : (BuyQty<SellQty ? (SellAvg-(lowerb/100.0))*(SellQty-BuyQty): ((lowerb/100.0)-BuyAvg)*(BuyQty-SellQty))) as MTMF,Expense from ${user}_BuySellsAgg LEFT JOIN  nse_tbt_snap  on ${user}_BuySellsAgg.Token==nse_tbt_snap.Token;\n\ndrop table IF EXISTS ${user}_BuySell;\ndrop table IF EXISTS ${user}_BuySellsAgg;\ndrop table IF EXISTS ${user}_TradeBook;\n" arguments="string user, long starttime, long endtime";
```

### NetBookConrevPositions

- Type: AMISCRIPT
- Return type: String
- Arguments: user String,starttime long,endtime long
- Owner: USER

```sql
CREATE PROCEDURE NetBookConrevPositions OFTYPE AMISCRIPT USE logging="verbose" script="\n\n    long startdt = formatDate(starttime, \"yyyyMMdd\", \"IST\");\n    long enddt   = formatDate(endtime, \"yyyyMMdd\", \"IST\");\n    long today   = formatDate(timestamp(), \"yyyyMMdd\", \"IST\");\n\n    drop table IF EXISTS ${user}_TradeBook;\n\n    CREATE PUBLIC TABLE ${user}_TradeBook (\n        server String BITMAP,\n        user String BITMAP,\n        sgroup String BITMAP,\n        frontend String BITMAP,\n        ip String BITMAP,\n        UID Long,\n        AutoNo Long,\n        InOutTag String BITMAP,\n        Exch String BITMAP,\n        PfName String BITMAP,\n        PfNo Integer,\n        Token Long,\n        InstType String BITMAP,\n        Symbol String BITMAP,\n        Expiry String BITMAP,\n        OptType String BITMAP,\n        StrikePrice float,\n        ProClient String BITMAP,\n        Acc String BITMAP,\n        Side String BITMAP,\n        ExchTimeStamp String,\n        SystemTimeStamp String,\n        OrderType Long,\n        OrderStatus String BITMAP,\n        Price Double,\n        FillPrice Double,\n        FillNumber Long,\n        FillQty Long,\n        LeavesQty Long,\n        OrderNo String,\n        LastShare Long,\n        ActualQty Long,\n        ExchOrderNo Long,\n        ErrorMsg String,\n        FilledLots Long,\n        PAN String BITMAP,\n        AlgoId Long,\n        AlgoCategory Long,\n        TradingSymbol String BITMAP,\n        NNF String,\n        BrokerId String,\n        NetBook String BITMAP,\n        TraderId Long,\n        LTP Double\n    ) USE NoBroadcast;\n\n    drop table IF EXISTS ${user}_conrevNetBookDelta;\n\n    CREATE PUBLIC TABLE ${user}_conrevNetBookDelta (\n        sgroup String BITMAP,\n        backend String BITMAP,\n        ip String BITMAP,\n        frontend String BITMAP,\n        user String BITMAP,\n        Acc String BITMAP,\n        PfNo Integer,\n        Exch String BITMAP,\n        Token Long,\n        Symbol String,\n        Expiry String BITMAP,\n        StrikePrice Float,\n        OptType String BITMAP,\n        InstType String BITMAP,\n        BuyQty Long,\n        BuyValue Double,\n        BuyAvg Double,\n        SellQty Long,\n        SellValue Double,\n        SellAvg Double,\n        NetPosition Long,\n        NetValue Double,\n        NetPrice Double,\n        LTP Double,\n        FLTP Double,\n        Vega Double,\n        Theta Double,\n        Gamma Double,\n        Delta Double,\n        Rho Double,\n        IV Double,\n        BPL Double,\n        MTM Double,\n        MTMF Double,\n        Expense Double,\n        NetBook String BITMAP,\n        RunTs String BITMAP,\n        LegGroupId String BITMAP,\n        LegRole String BITMAP,\n        LegSignal String BITMAP,\n        LegDiff Double,\n        LegQty Long,\n        TraderId Long\n    ) USE NoBroadcast;\n\n    if (startdt == today || enddt == today) {\n        insert into ${user}_TradeBook\n        FROM\n        select\n            strTrim(server) as server, strTrim(user) as user, strTrim(sgroup) as sgroup, strTrim(frontend) as frontend, strTrim(ip) as ip,\n            UID, AutoNo, strTrim(InOutTag) as InOutTag, strTrim(Exch) as Exch,\n            strTrim(PfName) as PfName, PfNo, Token, strTrim(InstType) as InstType, strTrim(Symbol) as Symbol, strTrim(Expiry) as Expiry, strTrim(OptType) as OptType,\n            StrikePrice, strTrim(ProClient) as ProClient, strTrim(Acc) as Acc, strTrim(Side) as Side, strTrim(ExchTimeStamp) as ExchTimeStamp,\n            strTrim(SystemTimeStamp) as SystemTimeStamp, OrderType, strTrim(OrderStatus) as OrderStatus, Price, FillPrice,\n            FillNumber, FillQty, LeavesQty, strTrim(OrderNo) as OrderNo, LastShare,\n            ActualQty, ExchOrderNo, strTrim(ErrorMsg) as ErrorMsg, FilledLots, strTrim(PAN) as PAN,\n            AlgoId, AlgoCategory, strTrim(TradingSymbol) as TradingSymbol, strTrim(NNF) as NNF, strTrim(BrokerId) as BrokerId,\n            strTrim(NetBook) as NetBook,\n            TraderId, LTP\n        from TradeBook\n        where parseDate(ExchTimeStamp, \"yyyy-MM-dd HH:mm:ss\", \"IST\") >= ${starttime}\n          && parseDate(ExchTimeStamp, \"yyyy-MM-dd HH:mm:ss\", \"IST\") <= ${endtime};\n    }\n\n    if (startdt != today || enddt != today) {\n        string tablname = \"TRADEBOOK\";\n\n        insert into ${user}_TradeBook\n        FROM\n        select\n            strTrim(server) as server, strTrim(user) as user, strTrim(sgroup) as sgroup, strTrim(frontend) as frontend, strTrim(ip) as ip,\n            UID, AutoNo, strTrim(InOutTag) as InOutTag, strTrim(Exch) as Exch,\n            strTrim(PfName) as PfName, PfNo, Token, strTrim(InstType) as InstType, strTrim(Symbol) as Symbol, strTrim(Expiry) as Expiry, strTrim(OptType) as OptType,\n            StrikePrice, strTrim(ProClient) as ProClient, strTrim(Acc) as Acc, strTrim(Side) as Side, strTrim(ExchTimeStamp) as ExchTimeStamp,\n            strTrim(SystemTimeStamp) as SystemTimeStamp, OrderType, strTrim(OrderStatus) as OrderStatus, Price, FillPrice,\n            FillNumber, FillQty, LeavesQty, strTrim(OrderNo) as OrderNo, LastShare,\n            ActualQty, ExchOrderNo, strTrim(ErrorMsg) as ErrorMsg, FilledLots, strTrim(PAN) as PAN,\n            AlgoId, AlgoCategory, strTrim(TradingSymbol) as TradingSymbol, strTrim(NNF) as NNF, strTrim(BrokerId) as BrokerId,\n            strTrim(NetBook) as NetBook,\n            TraderId, LTP\n        from ${tablname}\n        where parseDate(ExchTimeStamp, \"yyyy-MM-dd HH:mm:ss\", \"IST\") >= ${starttime}\n          && parseDate(ExchTimeStamp, \"yyyy-MM-dd HH:mm:ss\", \"IST\") <= ${endtime};\n          //&& ip != \"1.1.1.1\";\n    }\n\n    drop table IF EXISTS ${user}_BuySell;\n\n    create public table ${user}_BuySell as\n    SELECT\n        sgroup,\n        ip as backend,\n        server as ip,\n        frontend,\n        user,\n        Acc,\n        Exch,\n        0 as PfNo,\n        Token,\n        Symbol,\n        Expiry,\n        StrikePrice,\n        OptType,\n        ${user}_TradeBook.InstType as InstType,\n        (${user}_TradeBook.Side == \"BUY\" ? FillQty : 0) as BuyQty,\n        (${user}_TradeBook.Side == \"BUY\" ? FillQty * FillPrice : 0) as BuyValue,\n        (${user}_TradeBook.Side == \"SELL\" ? FillQty : 0) as SellQty,\n        (${user}_TradeBook.Side == \"SELL\" ? FillQty * FillPrice : 0) as SellValue,\n        (${user}_TradeBook.Side == \"BUY\" ? FillQty * FillPrice * ExpPer / 100.0 : 0) as BExpense,\n        (${user}_TradeBook.Side == \"SELL\" ? FillQty * FillPrice * ExpPer / 100.0 : 0) as SExpense,\n        ${user}_TradeBook.NetBook as NetBook,\n        TraderId\n    from ${user}_TradeBook\n    LEFT JOIN MasterExpenseParams\n        ON ${user}_TradeBook.Exch == MasterExpenseParams.Exchange\n       && ${user}_TradeBook.InstType == MasterExpenseParams.InstType\n       && ${user}_TradeBook.Side == MasterExpenseParams.Side\n    && user ~~ \"${user}\";\n\n    drop table IF EXISTS ${user}_BuySellsAgg;\n\n    create public table ${user}_BuySellsAgg as\n    select\n        sgroup, backend, ip, frontend, user, Acc, Exch, PfNo, Token,\n        NetBook, TraderId,\n        Symbol, Expiry, StrikePrice, OptType, InstType,\n        sum(BuyQty) as BuyQty,\n        sum(BuyValue) as BuyValue,\n        sum(SellQty) as SellQty,\n        sum(SellValue) as SellValue,\n        sum(BuyQty) - sum(SellQty) as NetPosition,\n        sum(SellValue) - sum(BuyValue) as NetValue,\n        sum(BuyQty) > 0 ? sum(BuyValue) / sum(BuyQty) : 0 as BuyAvg,\n        sum(SellQty) > 0 ? sum(SellValue) / sum(SellQty) : 0 as SellAvg,\n        (sum(SellValue) - sum(BuyValue)) / (sum(SellQty) - sum(BuyQty)) as NetPrice,\n        sum(BExpense) + sum(SExpense) as Expense\n    from ${user}_BuySell\n    group by\n        sgroup, backend, ip, frontend, user, Acc, Exch, PfNo, Token,\n        NetBook, TraderId,\n        Symbol, Expiry, StrikePrice, OptType, InstType;\n\n\n    drop table IF EXISTS ${user}_BuySell;\n    drop table IF EXISTS ${user}_TradeBook;\n\n" arguments="string user, long starttime, long endtime";
```

### NetBookMergeConrev

- Type: AMISCRIPT
- Return type: String
- Arguments: user String
- Owner: USER

```sql
CREATE PROCEDURE NetBookMergeConrev OFTYPE AMISCRIPT USE logging="verbose" script="    \n    drop table IF EXISTS ${user}_BuySellsAggC1;\n    create public table ${user}_BuySellsAggC1 as select sgroup,backend,ip,frontend,user,Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType,BuyQty,BuyValue,SellQty,SellValue,NetPosition,NetValue,NetPrice,BuyAvg,SellAvg,Expense,NetBook,TraderId,0.00 as AlgoBPL from ${user}_BuySellsAgg;\n\n    insert into  ${user}_BuySellsAggC1 from      select sgroup,backend,ip,frontend,user,Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType,BuyQty,BuyValue,SellQty,SellValue,NetPosition,NetValue,NetPrice,BuyAvg,SellAvg,Expense,NetBook,TraderId,(BPL==null?0:BPL) as AlgoBPL from ${user}_conrevNetBookDelta;\n\n    drop table IF EXISTS ${user}_BuySellsAggC2;\n    create public table ${user}_BuySellsAggC2 as select sum(BuyQty) as BuyQty,sum(BuyValue) as BuyValue,sum(SellQty) as SellQty,sum(SellValue) as SellValue,sum(BuyQty)-sum(SellQty) as NetPosition,sum(SellValue)-sum(BuyValue) as NetValue,(sum(BuyQty)>0 ? sum(BuyValue)/sum(BuyQty) : 0) as BuyAvg,(sum(SellQty)>0 ? sum(SellValue)/sum(SellQty) : 0) as SellAvg,((sum(SellQty)-sum(BuyQty))!=0? (sum(SellValue)-sum(BuyValue))/(sum(SellQty)-sum(BuyQty)): 0) as NetPrice,sum(Expense) as Expense,sum(AlgoBPL) as AlgoBPL,sgroup,backend,ip,frontend,user,Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType,TraderId,NetBook from  ${user}_BuySellsAggC1 group by sgroup,backend,ip,frontend,user,Acc,Exch,PfNo,Token,Symbol,Expiry,StrikePrice,OptType,InstType,TraderId,NetBook;\n\n    drop table IF EXISTS ${user}_NetBookConrev;\n\n    create public table ${user}_NetBookConrev as\n    select\n        NetBook,\n        sgroup, backend, ip, frontend, user, Acc,\n        ${user}_BuySellsAggC2.Exch as Exch,\n        PfNo,\n        ${user}_BuySellsAggC2.Token as Token,\n        Symbol, Expiry, StrikePrice, OptType,\n        TraderId,\n        InstType,\n        BuyQty, BuyValue, SellQty, SellValue,\n        NetPosition as NetQty,\n        NetValue, BuyAvg, SellAvg, NetPrice,\n        (LTP / 100.0) as LTP,\n        gVega * NetPosition as Vega,\n        gTheta * NetPosition as Theta,\n        gGamma * NetPosition as Gamma,\n        gDelta * NetPosition as Delta,\n        gRho * NetPosition as Rho,\n        gIV as IV,\n        lowerb / 100.0 as FLTP,\n        (AlgoBPL == null ? 0 : AlgoBPL) as AlgoBPL,\n        (BuyQty == SellQty\n            ? (SellValue - BuyValue)\n            : ((SellAvg - BuyAvg) * minimum(BuyQty, SellQty))\n        ) as TradeBPL,\n        (\n            (AlgoBPL == null ? 0 : AlgoBPL) +\n            (BuyQty == SellQty\n                ? (SellValue - BuyValue)\n                : ((SellAvg - BuyAvg) * minimum(BuyQty, SellQty))\n            )\n        ) as TotalBPL,\n        (\n            (AlgoBPL == null ? 0 : AlgoBPL) +\n            (BuyQty == SellQty\n                ? (SellValue - BuyValue)\n                : ((SellAvg - BuyAvg) * minimum(BuyQty, SellQty))\n            )\n        ) as BPL,\n        (BuyQty == SellQty\n            ? 0\n            : (BuyQty < SellQty\n                ? (SellAvg - (LTP / 100.0)) * (SellQty - BuyQty)\n                : ((LTP / 100.0) - BuyAvg) * (BuyQty - SellQty)\n              )\n        ) as MTM,\n        (BuyQty == SellQty\n            ? 0\n            : (BuyQty < SellQty\n                ? (SellAvg - (lowerb / 100.0)) * (SellQty - BuyQty)\n                : ((lowerb / 100.0) - BuyAvg) * (BuyQty - SellQty)\n              )\n        ) as MTMF,\n        Expense\n    from ${user}_BuySellsAggC2\n    LEFT JOIN nse_tbt_snap\n        on ${user}_BuySellsAggC2.Token == nse_tbt_snap.Token;\n\n    drop table IF EXISTS ${user}_BuySellsAggC1;\n    drop table IF EXISTS ${user}_BuySellsAggC2;\n" arguments="string user";
```

### netBookSnap

- Type: AMISCRIPT
- Return type: String
- Arguments: 
- Owner: USER

```sql
CREATE PROCEDURE netBookSnap OFTYPE AMISCRIPT USE logging="verbose" script="long ts=timestamp();insert into NetBookSnap (snapTime,sgroup,backend,ip,frontend,user,BPL,MTM,Expense) select ${ts} as snapTime,sgroup,backend,ip,frontend,user,sum(BPL) as BPL,sum(MTM) as MTM,sum(Expense) as Expense from NetBookC group by sgroup,backend,ip,frontend,user;" arguments="";
```

