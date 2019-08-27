from ib_insync import *

ib = IB()

def checkConnection():
   if ib.isConnected() != True:
        ib.connect('127.0.0.1', 7497, clientId=45)





def getMarketPrice(contract):
    #get market price of a contract
 
    checkConnection()

    ib.reqMktData(contract, '', False, False)
    ticker=ib.ticker(contract)
    ib.sleep(2)


    return ticker, ticker.marketPrice()

def createCacContract():
    #create contract for cac future expiring 20 sept 2019
    contract = Future(conId=372585961)
    ib.qualifyContracts(contract)
    return contract


checkConnection()

cac = createCacContract()

ticker, price = getMarketPrice(cac)
print(ticker)
print()
print(price)







