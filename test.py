from ib_insync import *
import sys

ib = IB()

def checkConnection():
   if ib.isConnected() != True:
        ib.connect('127.0.0.1', 7497, clientId=45)

def Cac_CreateContract():
    #create contract for cac future expiring 20 sept 2019
    contract = Future(localSymbol="MFCU9", exchange = "MONEP")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract

def SE_CreateContract():
    #create contract for S&P500 mini future expiring 20 sept 2019
    contract = Future(localSymbol="ESU9", exchange = "GLOBEX")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    
    return contract

def Nasdaq_CreateContract():
    #create contract for NASDAQ mini future expiring 20 dec 2019
    contract = Future(localSymbol="NQZ9", exchange = "GLOBEX")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract

def Russel_CreateContract():
    #create contract for Russel 2000 mini future expiring 20 sept 2019
    contract = Future(localSymbol="RTYU9", exchange = "GLOBEX")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract




def getMultipleMarketPrices(contracts):
    #determine if argument passed is single contract or list
    try:
        contractNumber = len(contracts)
    except TypeError:
        print("Error: called multipleMarketPrices function for single contract")
        print(contracts)
        sys.exit('used the wrong way to call contract, leaving application')

    #change this to change type of market data
    ib.reqMarketDataType(3) #1=live / 2= frozen / 3=delayed / 4=delayed frozen

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





checkConnection()

russel = Russel_CreateContract()
nasdaq = Nasdaq_CreateContract()
se = SE_CreateContract()

contracts = [russel, nasdaq, se]

prices = getMultipleMarketPrices(contracts)

russelPrice = prices[0]
nasdaqPrice = prices[1]
sePrice = prices[2]

print(russelPrice / nasdaqPr)
print(nasdaqPrice)
print(sePrice)

#russelPrice = getMarketPrice([russel, nasdaq])
#nasdaqPrice = getMarketPrice(nasdaq)
#sePrice = getMarketPrice(se)

#print(russelPrice)
#print(nasdaqPrice)
#print(sePrice)



