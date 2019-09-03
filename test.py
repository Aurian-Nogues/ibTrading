from ib_insync import *
import sys
import datetime



ib = IB()

def checkConnection():
   if ib.isConnected() != True:
       while True:
           print('Not connected, trying to connect')
           ib.connect('127.0.0.1', 7497, clientId=45)
           ib.sleep(2)
           if ib.isConnected() == True:
               print('Connected')
               break

def Cac_CreateContract():
    checkConnection()
    #create contract for cac future expiring 20 sept 2019
    contract = Future(localSymbol="MFCU9", exchange = "MONEP")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract

def Es_CreateContract():
    checkConnection()
    #create contract for S&P500 mini future expiring 20 sept 2019
    contract = Future(localSymbol="ESU9", exchange = "GLOBEX")
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
    contract = Future(localSymbol="RTYU9", exchange = "GLOBEX")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract

       
def getMarketPrice(contract):
    checkConnection()
    #get market price of a contract
 
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

russel = Russel_CreateContract()
russelPrice = getMarketPrice(russel)
print(russelPrice)

es = Es_CreateContract()
esPrice = getMarketPrice(es)
print(esPrice)