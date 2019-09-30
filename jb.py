from ib_insync import *
import csv

import time



#////////// generic functions ////////

ib = IB()

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



def getMarketPrice(contract):
    checkConnection()
    #change this to change type of market data
    ib.reqMarketDataType(1) #1=live / 2= frozen / 3=delayed / 4=delayed frozen
 
    

    ib.reqMktData(contract, '', False, False)
    ticker=ib.ticker(contract)
    ib.sleep(2)

    return ticker.marketPrice()




#strategy specific

def startJb(contract, referencePrice):
    checkConnection()

    # action (str) – ‘BUY’ or ‘SELL’.
    # quantity (float) – Size of order.
    # limitPrice (float) – Limit price of entry order.
    # takeProfitPrice (float) – Limit price of profit order.
    # stopLossPrice (float) – Stop price of loss order.
    
    #create 2 bracker orders
    # order = ib.bracketOrder(action, quantity, limitPrice, takeProfitPrice, stopLossPrice)

    action = 'SELL'
    quantity = 1
    limitPrice = referencePrice + 0.21
    takeProfitPrice = referencePrice + 0.21 - 0.10
    stopLossPrice = referencePrice + 0.21 + 0.20
    upOrder = ib.bracketOrder(action = action, quantity = quantity, limitPrice = limitPrice, takeProfitPrice = takeProfitPrice, stopLossPrice = stopLossPrice)

    #ocaGroup = ocaGroup, ocaType = ocaType

    action = 'BUY'
    quantity = 1
    limitPrice = referencePrice -0.31
    takeProfitPrice = referencePrice -0.31 + 0.10
    stopLossPrice = referencePrice -0.31 - 0.20
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

    return upTrade, downTrade


    

def sendJbOrders(orders):
    #variables to store parent trades
    parentTrade = None

    #send orders
    for o in orders:
        trade = ib.placeOrder(contract, o)

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



def JbClosing(upTrade, downTrade, Contract):
    
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
    JbClosePositions(contract)
    #write logs
    jbSummary()



    

    #log summary of executed trades
    jbSummary()

def JbClosePositions(contract):
    positions = ib.positions()

    #figure out  if we have a position
    for position in positions:

        if position[1] == contract:
            quantity = position[2]

            #prepare trade
            if quantity >0:
                direction = "Sell"
            elif quantity < 0:
                direction = "Buy"
                quantity = abs(quantity)
            
            order = MarketOrder(direction, quantity)

            #send trade
            trade = ib.placeOrder(contract,order)

        






    

def jbSummary():
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




checkConnection()

contract = jb_CreateContract()
price = getMarketPrice(contract)
if price =="nan":
    print('Price was nan')
    
upTrade, downTrade = startJb(contract, price)
ib.sleep(2)
JbClosing(upTrade, downTrade, contract)









