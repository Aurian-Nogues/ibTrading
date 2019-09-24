from ib_insync import *
import time

ib = IB()

def Cac_CreateContract():
    checkConnection()
    #create contract for cac future expiring 20 sept 2019
    contract = Future(localSymbol="MFCV9", exchange = "MONEP")
    #ib.reqContractDetails(contract)
    try:
        ib.qualifyContracts(contract)
    except :
        time.sleep(5)
        checkConnection()
        ib.qualifyContracts(contract)
    






    return contract

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



def placeMarketOrder(contract, direction, quantity, strategy):
    checkConnection()
    order = MarketOrder(direction, quantity)
    trade = ib.placeOrder(contract, order)
    ib.sleep(1)
    print('Market order placed, strategy is ' + str(strategy))
    tradeLog = trade.log

    print(tradeLog)

cac = Cac_CreateContract()

placeMarketOrder(cac, "Buy", 1, "CAC_ON")

