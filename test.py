from ib_insync import *

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


#strategy specific

def sendJbOrders(contract, referencePrice):

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

    upOrderId = upOrder[0].orderId
    downOrderId = downOrder[0].orderId


    #add once cancel all parameters on parent orders
    ocaGroup = 'JB ' + str(upOrderId)

    # 1	Cancel all remaining orders with block.*
    # 2	Remaining orders are proportionately reduced in size with block.*
    # 3	Remaining orders are proportionately reduced in size with no block.
    ocaType = 2

    upOrder[0].ocaGroup = ocaGroup
    upOrder[0].ocaType = ocaType
    downOrder[0].ocaGroup = ocaGroup
    downOrder[0].ocaType = ocaType

    #send orders
    for o in upOrder:
        trade = ib.placeOrder(contract, o)

    for o in downOrder:
        trade = ib.placeOrder(contract, o)
    
    return upOrder, downOrder


def JbClosing(upOrder, downOrder):
    #get status of orders
    pass










checkConnection()

contract = jb_CreateContract()

#TODO change this to get reference price, careful when price returned is nan
price = getMarketPrice(contract)


upOrder, downOrder = sendJbOrders(contract, price)
JbClosing(upOrder, downOrder)





