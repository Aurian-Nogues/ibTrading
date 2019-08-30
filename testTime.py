import datetime
import schedule, time
from ib_insync import *

ib = IB()

def checkConnection():
   if ib.isConnected() != True:
        ib.connect('127.0.0.1', 7497, clientId=45) # TWS
        #ib.connect('127.0.0.1', 4002, clientId=45) # Gateway

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

def futArb(contracts):
    prices = getMultipleMarketPrices(contracts)
    print(contracts)
    print(prices)
    ratio = prices[0] / prices[1]
    print(ratio)




checkConnection()

nasdaq = Nasdaq_CreateContract()
russel = Russel_CreateContract()

contracts = [nasdaq, russel]
schedule.every(5).seconds.do(futArb, contracts)
#schedule.every().monday.at("09:00").do(futArb, contracts)


#loop to keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(1)
