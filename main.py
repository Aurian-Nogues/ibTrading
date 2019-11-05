import datetime, time
from ib_insync import *
import schedule, time, sys, math
import csv
import re


ib = IB()


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////Contracts/////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def Cac_CreateContract():
    checkConnection()
    #create contract for cac future expiring 20 sept 2019
    contract = Future(localSymbol="MFCX9", exchange = "MONEP")
    #ib.reqContractDetails(contract)
    try:
        ib.qualifyContracts(contract)
    except :
        time.sleep(5)
        checkConnection()
        ib.qualifyContracts(contract)
    return contract

def Es_CreateContract():
    checkConnection()
    #create contract for S&P500 mini future expiring 20 sept 2019
    contract = Future(localSymbol="ESZ9", exchange = "GLOBEX")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    
    return contract

def Nasdaq_CreateContract():
    checkConnection()
    #create contract for NASDAQ mini future expiring 20 dec 2019
    contract = Future(localSymbol="NQZ9", exchange = "GLOBEX")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract

def Russel_CreateContract():
    checkConnection()
    #create contract for Russel 2000 mini future expiring 20 sept 2019
    contract = Future(localSymbol="RTYZ9", exchange = "GLOBEX")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract

def jb_CreateContract():
    checkConnection()
    #create contract for Japanese Bond expirint 13/12/2019
    contract = Future(localSymbol="164120001", exchange = "OSE.JPN")
    #ib.reqContractDetails(contract)
    try:
        ib.qualifyContracts(contract)
    except :
        time.sleep(5)
        checkConnection()
        ib.qualifyContracts(contract)
    return contract

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////Shared functions/////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def checkConnection():
   if ib.isConnected() != True:
       while True:
           print('Not connected, trying to connect')
           ib.connect('127.0.0.1', 7497, clientId=45)
           #ib.connect('127.0.0.1', 4002, clientId=45) # Gateway
           ib.sleep(2)
           if ib.isConnected() == True:
               print('Connected')
               break
        


def getPosition(contract):
    #checkConnection()
    #returns the position for a given contract
    #returns None if there is no position matching the contract

    positions = ib.positions()
    #position structure:
#   [0] = account
#   [1] = contract
#   [2] = position
#   [3] = avgcost
    result = None

    for position in positions:
        if position[1] == contract:
            result = position
    return result


def getMarketPrice(contract):
    checkConnection()
    #change this to change type of market data
    ib.reqMarketDataType(1) #1=live / 2= frozen / 3=delayed / 4=delayed frozen
 
    

    ib.reqMktData(contract, '', False, False)
    ticker=ib.ticker(contract)
    ib.sleep(2)

    return ticker.marketPrice()


def getMultipleMarketPrices(contracts):
    checkConnection()
    #determine if argument passed is single contract or list
    try:
        contractNumber = len(contracts)
    except TypeError:
        print("Error: called multipleMarketPrices function for single contract")
        print(contracts)
        sys.exit('used the wrong way to call contract, leaving application')

    #change this to change type of market data
    ib.reqMarketDataType(1) #1=live / 2= frozen / 3=delayed / 4=delayed frozen

    #get market price of a contracts
    checkConnection()

    tickersList = []
    priceList=[]

    for contract in contracts:

        ib.reqMktData(contract, '', False, False)
        tickersList.append(ib.ticker(contract))

    ib.sleep(2)

    for ticker in tickersList:
        priceList.append(ticker.marketPrice())

    return priceList


def placeMarketOrder(contract, direction, quantity, strategy):
    checkConnection()
    order = MarketOrder(direction, quantity)
    trade = ib.placeOrder(contract, order)
    ib.sleep(1)
    print('Market order placed, strategy is ' + str(strategy))
    tradeLog = trade.log

    #write trade in log
    writeLog(tradeLog, contract, direction, strategy)



def writeLog(tradeLog, contract, direction, strategy):
    for entry in tradeLog:
        if entry.message != '':
                #get filled quantity
                text = entry.message
                try:
                        found = re.search('Fill (.+?)@', text).group(1)
                        execQtyLog = found
                except:
                        print('Execution quantity not found in message')
                        execQtyLog = 'Qty not found in trade log'

                #define log entries    
                strategy = strategy
                timeLog = entry.time
                contractLog = contract.symbol
                conIdLog = contract.conId
                expiryLog = contract.lastTradeDateOrContractMonth
                directionLog = direction
                execPriceLog = entry.message.split('@', 1)[1]
                execQtyLog = execQtyLog

                #build entry and append it to trade logs
                logEntry = [
                        strategy,
                        timeLog,
                        contractLog,
                        conIdLog,
                        expiryLog,
                        directionLog,
                        execPriceLog,
                        execQtyLog
                ]

                if strategy == 'CAC_ON':
                    with open('CAC_ON_trading_log.csv', 'a') as f:
                            writer = csv.writer(f, lineterminator = '\n')
                            writer.writerow(logEntry)
                elif strategy == 'FutArb':
                    with open('FutArb_trading_log.csv', 'a') as f:
                            writer = csv.writer(f, lineterminator = '\n')
                            writer.writerow(logEntry)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////CAC/////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def Cac_eveningOpen(contract):
    checkConnection()

    print('\n')
    position = getPosition(contract)
    strategy = 'CAC_ON'
    if position is None:
        print('opening position on CAC_ON...')
        direction = 'Buy'
        quantity = 1
        placeMarketOrder(contract, direction, quantity, strategy)


    else:
        print('Error, there already is a position open in CAC_ON')
        print('liquidating position and stopping algo')
        liquidatePosition(contract, strategy)
        ib.disconnect()
        sys.exit()


def Cac_morningClose(contract):
    checkConnection()

    print('\n')
    print('Closing position on CAC_ON...')
    strategy = 'CAC_ON'
    position = getPosition(contract)
    if position is not None:
        liquidatePosition(contract, strategy)

    else:
        print('Error, there is no position to close on CAC_ON')
        print('Algo is still running, will open position this evening')


def Cac_master(action):
    checkConnection()
    #This functions determines wether to open or close a trade in CAC_ON

    cac = Cac_CreateContract()
    #positionCac = getPosition(cac)


    if action == "Open":
            Cac_eveningOpen(cac)
    elif action == "Close":
            Cac_morningClose(cac)



#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////FUTARB/////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def definecontractsFutArb():
    russel = Russel_CreateContract()
    es = Es_CreateContract()
    contractsFutArb = [russel, es]
    return contractsFutArb


def futArbInitial():
    checkConnection()
    global initComboPrice
    global futArb_state

    contracts = definecontractsFutArb()


    today = datetime.datetime.today()
    weekday = today.weekday() #returns integer, monday=0, tuesday=1...
    
    if weekday > 5: #if today is monday to friday
        return
        
        
    futArb_state = 'closed'

    prices = getMultipleMarketPrices(contracts)
    russelPrice = prices[0]
    esPrice = prices[1]
    initComboPrice = (esPrice - 2*russelPrice) * 50 + 20000

    print("/////////Triggered futArb///////")
    print('futArb state = ' + str(futArb_state))
    print('Russel price = ' + str(russelPrice))
    print('ES price = ' + str(esPrice))
    print('combo price = ' + str(initComboPrice))
    print('//////////////////////////////// \n')

    #write to log
    
    logStrategy = 'futArb'
    logTime = datetime.datetime.now()
    logRusselPrice = russelPrice
    logEsPrice = esPrice
    logComboOpening = initComboPrice
    logCurrentCombo = initComboPrice
    logLowerBoundary = 'n/a'
    logHigherBoundary = 'n/a'
    logState = futArb_state 
    logConclusion = 'Triggered futArb'

    logEntry = [logStrategy, logTime, logRusselPrice, logEsPrice,logComboOpening, logCurrentCombo, logLowerBoundary, logHigherBoundary, logState, logConclusion]
    logFutArbMonitoring(logEntry)

      

def futArbMonitor():
    checkConnection()
    global futArb_state
    global initComboPrice
    global futarb_openType

    contracts = definecontractsFutArb()

    russel = contracts[0]
    es = contracts[1]

    #tests---------------------------------------
    #futArb_state = 'open'
    #-------------------------------------------

    if futArb_state == 'non_triggerable': #strategy non triggerable because already closed
        print('futarb is not triggerable')
        print('either we did not go through futArbInitial or P&L is <> $500')
        logConclusion = 'Did not trade, state was non triggerable'

        russelPrice = 'N/A'
        esPrice = 'N/A'
        initComboPrice = 'N/A'
        currentComboPrice = 'N/A'
        lowBoudary = 'N/A'
        highBoundary = 'N/A'

    if futArb_state == 'open': #check if p$L is <> $500 so we should close

        prices = getMultipleMarketPrices(contracts)
        russelPrice = prices[0]
        esPrice = prices[1]
        currentComboPrice = (esPrice - 2*russelPrice) * 50 + 20000

        if futarb_openType == "low":
            lowBoudary = initComboPrice -500 -250 #cut position if P&L is > 500
            highBoundary = initComboPrice + 500 - 250 #cut position if P&L is > 500
        elif futarb_openType == "high":
            lowBoudary = initComboPrice -500 + 250 #cut position if P&L is > 500
            highBoundary = initComboPrice + 500 + 250 #cut position if P&L is > 500



        #tests---------------------------------------
        #currentComboPrice = initComboPrice -800
        #-------------------------------------------

        if currentComboPrice <= lowBoudary:
            print('FutArb reached low boundary, closing position...')
            liquidatePosition(es, 'FutArb')
            liquidatePosition(russel, 'FutArb')
            futArb_state = 'non_triggerable'

            logConclusion = 'Combo price below low boundary, closed position'


        elif currentComboPrice >= highBoundary:
            print('FutArb reached high boundary, closing position...')
            liquidatePosition(es, 'FutArb')
            liquidatePosition(russel, 'FutArb')
            futArb_state = 'non_triggerable'
            logConclusion = 'Combo price above high boundary, closed position'
        
        else:
            logConclusion = 'Combo price within boundaries, did nothing'
    
    if futArb_state == 'closed': #check if we should be opening a position

        prices = getMultipleMarketPrices(contracts)
        russelPrice = prices[0]
        esPrice = prices[1]
        currentComboPrice = (esPrice - 2*russelPrice) * 50 + 20000

        lowBoudary = initComboPrice -250
        highBoundary = initComboPrice + 250

        #tests---------------------------------------
        #currentComboPrice = initComboPrice -300
        #-------------------------------------------

        if currentComboPrice <= lowBoudary:
            if currentComboPrice <= lowBoudary - 100:
                currentTimestamp = datetime.datetime.now()
                logConclusion = 'Combo price below low boundary - 50, did nothing'
            else:
                print('futArb: opening position -1ES +2RTY')
                placeMarketOrder(es, "Sell", 1, 'FutArb')
                placeMarketOrder(russel, "Buy", 2, 'FutArb')
                futArb_state = 'open'
                futarb_openType = "low"
                logConclusion = 'Combo price below low boundary, opened a position'
            

        elif currentComboPrice >= highBoundary:
            if currentComboPrice >= highBoundary + 100:
                currentTimestamp = datetime.datetime.now()
                logConclusion = 'Combo price above high boundary + 50, did nothing'
            else:

                print('futArb: opening position +1ES -2RTY')
                placeMarketOrder(es, "Buy", 1, 'FutArb')
                placeMarketOrder(russel, "Sell", 2, 'FutArb')
                futArb_state = 'open'
                futarb_openType = "high"
                logConclusion = 'Combo price above high boundary, opened a position'
            
        
        else:
            currentTimestamp = datetime.datetime.now()
            logConclusion = 'Combo price within boundaries, did nothing'

    
        #write to log
    
    logStrategy = 'futArb'
    logTime = datetime.datetime.now()
    logRusselPrice = russelPrice
    logEsPrice = esPrice
    logComboOpening = initComboPrice
    logCurrentCombo = currentComboPrice
    logLowerBoundary = lowBoudary
    logHigherBoundary = highBoundary
    logState = futArb_state 

    logEntry = [logStrategy, logTime, logRusselPrice, logEsPrice,logComboOpening, logCurrentCombo, logLowerBoundary, logHigherBoundary, logState, logConclusion]
    logFutArbMonitoring(logEntry)



def futArbTimingClose():
    checkConnection()
    global futArb_state
    global futarb_openType

    contracts = definecontractsFutArb()
    russel = contracts[0]
    es = contracts[1]

    if futArb_state == 'open':
        print('FutArb timing over, liquidating positions')
        liquidatePosition(es, 'FutArb')
        liquidatePosition(russel, 'FutArb')
        futArb_state = 'non_triggerable'
        logConclusion = 'Position was open when time expired, closed it'

    elif futArb_state == 'closed':
        print("Futarb time window closed without opening position")
        futArb_state = 'non_triggerable'
        logConclusion = 'Futarb time window closed without opening position'
    else:
        logConclusion = 'Futarb was non triggerable at time of closing'
    
            #write to log
    
    logStrategy = 'futArb'
    logTime = datetime.datetime.now()
    logRusselPrice = 'N/A'
    logEsPrice = 'N/A'
    logComboOpening = 'N/A'
    logCurrentCombo = 'N/A'
    logLowerBoundary = 'N/A'
    logHigherBoundary = 'N/A'
    logState = futArb_state 

    futarb_openType = None
    logEntry = [logStrategy, logTime, logRusselPrice, logEsPrice,logComboOpening, logCurrentCombo, logLowerBoundary, logHigherBoundary, logState, logConclusion]
    logFutArbMonitoring(logEntry)


def logFutArbMonitoring(logList):
    #13 entries
    logEntry = []
    for entry in logList:
        logEntry.append(entry)

    with open('FutArb_prices_monitoring.csv', 'a') as f:
        writer = csv.writer(f, lineterminator = '\n')
        writer.writerow(logEntry)



def liquidatePosition(contract, strategy):
    position = getPosition(contract)
    quantity = position[2]
    if quantity >0:
        direction = "Sell"
    elif quantity < 0:
        direction = "Buy"
        quantity = abs(quantity)


    placeMarketOrder(contract,direction, quantity, strategy )
    print(str(strategy) + ', ' + 'Liquidation order placed')
    

def test():
    print("working")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////Japanese bonds/////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def getJbReferencePrice():

    today = datetime.datetime.today()
    weekday = today.weekday() #returns integer, monday=0, tuesday=1...
    
    if weekday > 5: #if today is monday to friday
        return

    global jbContract
    global jbRefPrice
    
    checkConnection()
    
    jbContract = jb_CreateContract()
    jbRefPrice = getMarketPrice(jbContract)
    while True:
        if math.isnan(jbRefPrice):
            ib.sleep(2)
            print("Could not recover price, trying again")
            checkConnection()
            jbRefPrice = getMarketPrice(jbContract)
        else:
            print("Successfully got JB price : " + str(jbRefPrice))
            break

    print('Started JB, reference price is ' + str(jbRefPrice))
    


def startJb():
    today = datetime.datetime.today()
    weekday = today.weekday() #returns integer, monday=0, tuesday=1...
    
    if weekday > 5: #if today is monday to friday
        return

    checkConnection()

    global upTrade
    global downTrade
    global jbRefPrice
    global jbContract
    
    # action (str) – ‘BUY’ or ‘SELL’.
    # quantity (float) – Size of order.
    # limitPrice (float) – Limit price of entry order.
    # takeProfitPrice (float) – Limit price of profit order.
    # stopLossPrice (float) – Stop price of loss order.
    
    #create 2 bracker orders
    # order = ib.bracketOrder(action, quantity, limitPrice, takeProfitPrice, stopLossPrice)

    action = 'SELL'
    quantity = 1
    # limitPrice = jbRefPrice + 0.21
    # takeProfitPrice = jbRefPrice + 0.21 - 0.10
    # stopLossPrice = jbRefPrice + 0.21 + 0.20
    limitPrice = jbRefPrice + 0.11
    takeProfitPrice = jbRefPrice + 0.11 - 0.10
    stopLossPrice = jbRefPrice + 0.11 + 0.20




    upOrder = ib.bracketOrder(action = action, quantity = quantity, limitPrice = limitPrice, takeProfitPrice = takeProfitPrice, stopLossPrice = stopLossPrice)

    #ocaGroup = ocaGroup, ocaType = ocaType

    action = 'BUY'
    quantity = 1
    # limitPrice = jbRefPrice -0.31
    # takeProfitPrice = jbRefPrice -0.31 + 0.10
    # stopLossPrice = jbRefPrice -0.31 - 0.20
    limitPrice = jbRefPrice -0.11
    takeProfitPrice = jbRefPrice -0.11 + 0.10
    stopLossPrice = jbRefPrice -0.11 - 0.20



    downOrder = ib.bracketOrder(action = action, quantity = quantity, limitPrice = limitPrice, takeProfitPrice = takeProfitPrice, stopLossPrice = stopLossPrice)

    # #add once cancel all parameters on parent orders
    # upOrderId = upOrder[0].orderId
    # ocaGroup = 'JB ' + str(upOrderId)

    # # 1	Cancel all remaining orders with block.*
    # # 2	Remaining orders are proportionately reduced in size with block.*
    # # 3	Remaining orders are proportionately reduced in size with no block.
    # ocaType = 2

    # upOrder[0].ocaGroup = ocaGroup
    # upOrder[0].ocaType = ocaType
    # downOrder[0].ocaGroup = ocaGroup
    # downOrder[0].ocaType = ocaType

    upTrade = sendJbOrders(upOrder)
    downTrade = sendJbOrders(downOrder)

    print("Sent orders to JB")


def sendJbOrders(orders):
    checkConnection()
    global jbContract
    jbContract = jb_CreateContract()

    #variables to store parent trades
    parentTrade = None

    #send orders
    for o in orders:
        trade = ib.placeOrder(jbContract, o)

        #label child or parent order
        parentId = trade.order.parentId
        if parentId == 0:
            orderRef = trade.order.orderId
            orderGroup = 'Parent order ' + str(orderRef)
        else:
            orderGroup = 'Child order ' + str(parentId)

        #define which price is relevant, limit orders use lmtPrice, stop loss orders use auxPrice. The one not used is set at 1.7976931348623157e+308 in ib
        limitPrice = trade.order.lmtPrice
        if limitPrice < 10000000:
            price = limitPrice
        else:
            price = trade.order.auxPrice


        #Build log entry and add it to logs
        strategyLog = 'JGB'
        timeLog = trade.log[0].time
        contractLog = trade.contract.symbol
        groupLog = orderGroup
        directionLog = trade.order.action
        quantityLog = trade.order.totalQuantity
        priceLog = price
        
        logEntry = [
            strategyLog,
            timeLog,
            contractLog,
            groupLog,
            directionLog,
            quantityLog,
            priceLog
        ]

        writeJbLog(logEntry, 'Action')

        #store the first trade (which is the parent one) 
        if parentTrade == None:
            parentTrade = trade
    
    return parentTrade


def JbClosing():

    today = datetime.datetime.today()
    weekday = today.weekday() #returns integer, monday=0, tuesday=1...
    
    if weekday > 5: #if today is monday to friday
        return
    checkConnection()
    global upTrade
    global downTrade
    
    #get up and down trades order Id. If the trade is not active anymore orderId is 0
    upTradeId = upTrade.order.orderId
    downTradeId = downTrade.order.orderId
    
    #get all session orders
    orders = ib.orders()

    #if orders are still open, cancel them
    for order in orders:
        if (order.orderId == upTradeId) or (order.orderId == downTradeId):
            ib.sleep(2)
            ib.cancelOrder(order)

    
    #If positions are open, close them
    JbClosePositions()

    ib.sleep(5)
    #write logs
    jbSummary()

    print('Closed JB and wrote logs')



def JbClosePositions():
    global jbContract
    jbContract = jb_CreateContract()

    positions = ib.positions()

    #figure out  if we have a position
    for position in positions:

        if position[1] == jbContract:
            quantity = position[2]

            #prepare trade
            if quantity >0:
                direction = "Sell"
            elif quantity < 0:
                direction = "Buy"
                quantity = abs(quantity)
            
            order = MarketOrder(direction, quantity)

            #send trade
            ib.placeOrder(jbContract,order)


def jbSummary():
    checkConnection()
    #recover exec summary, build P&L and logs

    dailyTrades = ib.fills() #returns a list of objects where [0] is contract and [1] is exec details

    for trade in dailyTrades:
        contract = trade[0]
        execDetails = trade[1]
        if contract.symbol == 'JGB':
            #build a log entry

            strategyLog = 'JGB'
            timeLog = execDetails.time
            contractLog = contract.symbol
            directionLog = execDetails.side
            quantityLog = execDetails.shares
            priceLog = execDetails.avgPrice

            logEntry = [
                strategyLog,
                timeLog,
                contractLog,
                directionLog,
                quantityLog,
                priceLog
            ]

            writeJbLog(logEntry, "Trade")


def writeJbLog(logEntry, logType):

    if logType == 'Trade': 
        with open('JB_trade_log.csv', 'a') as f:
            writer = csv.writer(f, lineterminator = '\n')
            writer.writerow(logEntry)
    
    if logType == 'Action':
        with open('JB_action_log.csv', 'a') as f:
            writer = csv.writer(f, lineterminator = '\n')
            writer.writerow(logEntry)






#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////APP/////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def main():
    checkConnection()

# #-------Start CAC_on strategy--------
# #open position at 17:35 paris time, close it next day at 08:59 paris time


#     #schedule.every(3).seconds.do(Cac_master, "Open")
#     #schedule.every().day.at("17:39").do(Cac_master, "Open")
#     #schedule.every().day.at("17:40").do(Cac_master, "Close") 


    schedule.every().monday.at("08:59").do(Cac_master, "Close")
    schedule.every().monday.at("17:35").do(Cac_master, "Open")
    schedule.every().tuesday.at("08:59").do(Cac_master, "Close")
    schedule.every().tuesday.at("17:35").do(Cac_master, "Open")
    schedule.every().wednesday.at("08:59").do(Cac_master, "Close")
    schedule.every().wednesday.at("17:35").do(Cac_master, "Open")
    schedule.every().thursday.at("08:59").do(Cac_master, "Close")
    schedule.every().thursday.at("17:35").do(Cac_master, "Open")
    schedule.every().friday.at("08:59").do(Cac_master, "Close")
    schedule.every().friday.at("17:35").do(Cac_master, "Open")

# #-------Start futArb strategy--------
# #at 15:00 Paris time check the spread
# #if spread deviates by +/- $250 in the next hour open a position
# #if P&L is +/- $500 close position
# #if after 1 hour position is still open, close it


    global futArb_state
    global initComboPrice
    global futarb_openType

    futArb_state = 'non_triggerable'
    initComboPrice = None
    futarb_openType = None

 
    

    schedule.every().day.at("15:00").do(futArbInitial)
    schedule.every().day.at("15:01").do(futArbMonitor)
    schedule.every().day.at("15:02").do(futArbMonitor)
    schedule.every().day.at("15:03").do(futArbMonitor)
    schedule.every().day.at("15:04").do(futArbMonitor)
    schedule.every().day.at("15:05").do(futArbMonitor)
    schedule.every().day.at("15:06").do(futArbMonitor)
    schedule.every().day.at("15:07").do(futArbMonitor)
    schedule.every().day.at("15:08").do(futArbMonitor)
    schedule.every().day.at("15:09").do(futArbMonitor)
    schedule.every().day.at("15:10").do(futArbMonitor)
    schedule.every().day.at("15:11").do(futArbMonitor)
    schedule.every().day.at("15:12").do(futArbMonitor)
    schedule.every().day.at("15:13").do(futArbMonitor)
    schedule.every().day.at("15:14").do(futArbMonitor)
    schedule.every().day.at("15:15").do(futArbMonitor)
    schedule.every().day.at("15:16").do(futArbMonitor)
    schedule.every().day.at("15:17").do(futArbMonitor)
    schedule.every().day.at("15:18").do(futArbMonitor)
    schedule.every().day.at("15:19").do(futArbMonitor)
    schedule.every().day.at("15:20").do(futArbMonitor)
    schedule.every().day.at("15:21").do(futArbMonitor)
    schedule.every().day.at("15:22").do(futArbMonitor)
    schedule.every().day.at("15:23").do(futArbMonitor)
    schedule.every().day.at("15:24").do(futArbMonitor)
    schedule.every().day.at("15:25").do(futArbMonitor)
    schedule.every().day.at("15:26").do(futArbMonitor)
    schedule.every().day.at("15:27").do(futArbMonitor)
    schedule.every().day.at("15:28").do(futArbMonitor)
    schedule.every().day.at("15:29").do(futArbMonitor)
    schedule.every().day.at("15:30").do(futArbMonitor)
    schedule.every().day.at("15:31").do(futArbMonitor)
    schedule.every().day.at("15:32").do(futArbMonitor)
    schedule.every().day.at("15:33").do(futArbMonitor)
    schedule.every().day.at("15:34").do(futArbMonitor)
    schedule.every().day.at("15:35").do(futArbMonitor)
    schedule.every().day.at("15:36").do(futArbMonitor)
    schedule.every().day.at("15:37").do(futArbMonitor)
    schedule.every().day.at("15:38").do(futArbMonitor)
    schedule.every().day.at("15:39").do(futArbMonitor)
    schedule.every().day.at("15:40").do(futArbMonitor)
    schedule.every().day.at("15:41").do(futArbMonitor)
    schedule.every().day.at("15:42").do(futArbMonitor)
    schedule.every().day.at("15:43").do(futArbMonitor)
    schedule.every().day.at("15:44").do(futArbMonitor)
    schedule.every().day.at("15:45").do(futArbMonitor)
    schedule.every().day.at("15:46").do(futArbMonitor)
    schedule.every().day.at("15:47").do(futArbMonitor)
    schedule.every().day.at("15:48").do(futArbMonitor)
    schedule.every().day.at("15:49").do(futArbMonitor)
    schedule.every().day.at("15:50").do(futArbMonitor)
    schedule.every().day.at("15:51").do(futArbMonitor)
    schedule.every().day.at("15:52").do(futArbMonitor)
    schedule.every().day.at("15:53").do(futArbMonitor)
    schedule.every().day.at("15:54").do(futArbMonitor)
    schedule.every().day.at("15:55").do(futArbMonitor)
    schedule.every().day.at("15:56").do(futArbMonitor)
    schedule.every().day.at("15:57").do(futArbMonitor)
    schedule.every().day.at("15:58").do(futArbMonitor)
    schedule.every().day.at("15:59").do(futArbMonitor)


    schedule.every().day.at("16:00").do(futArbTimingClose)



    #-------Start Japanese bonds strategy--------

    # get reference price at 20:00 Paris time D-1
    # place trades before execution window
    # window is 1:45 am to 7:00 am
    # at 7:00 am close all positions and orders


    global upTrade
    global downTrade
    global jbRefPrice

    schedule.every().day.at("00:32").do(getJbReferencePrice)
    schedule.every().day.at("00:34").do(startJb)
    schedule.every().day.at("07:00").do(JbClosing)






    #loop to keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)






if __name__ == "__main__":
    main()

