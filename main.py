import datetime
from ib_insync import *
import pprint
import schedule, time, sys
import csv
import re


ib = IB()

#define global variables
cacOn_State = ''


#//////// contracts /////////

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


#//////////////////////////////


def checkConnection():
   if ib.isConnected() != True:
        ib.connect('127.0.0.1', 7497, clientId=45) # TWS
        #ib.connect('127.0.0.1', 4002, clientId=45) # Gateway


def getPosition(contract):
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
    #get market price of a contract
 
    checkConnection()

    ib.reqMktData(contract, '', False, False)
    ticker=ib.ticker(contract)
    ib.sleep(2)

    return ticker.marketPrice()


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


def placeMarketOrder(contract, direction, quantity, strategy):
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

                #build entry and append it to trade log
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
                with open('CAC_ON_trading_log.csv', 'a') as f:
                        writer = csv.writer(f, lineterminator = '\n')
                        writer.writerow(logEntry)


def liquidatePosition(contract, strategy):
    position = getPosition(contract)
    quantity = position[2]
    placeMarketOrder(contract,'Sell', quantity, strategy )
    print('Liquidation order placed')


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


def Cac_master(contract):
    #This functions determines wether to open or close a trade in CAC_ON

    global cacOn_State

    if cacOn_State == 'Closed':
            Cac_eveningOpen(contract)
            cacOn_State = 'Open'
    elif cacOn_State == 'Open':
            Cac_morningClose(contract)
            cacOn_State = 'Closed'



#//////////// app ///////////////////////


def main():

    #-------Start CAC_on strategy--------

    checkConnection()

    cac = Cac_CreateContract()
    positionCac = getPosition(cac)
   
    global cacOn_State
    if positionCac is None:
        cacOn_State = 'Closed'
    else:
        cacOn_State = 'Open'

    schedule.every(5).seconds.do(Cac_master, cac)
    #schedule.every().friday.at("12:40").do(Cac_master, cac)

#     schedule.every().monday.at("09:00").do(Cac_master, cac)
#     schedule.every().monday.at("17:00").do(Cac_master, cac)
#     schedule.every().tuesday.at("09:00").do(Cac_master, cac)
#     schedule.every().tuesday.at("17:00").do(Cac_master, cac)
#     schedule.every().wednesday.at("09:00").do(Cac_master, cac)
#     schedule.every().wednesday.at("17:00").do(Cac_master, cac)
#     schedule.every().thursday.at("09:00").do(Cac_master, cac)
#     schedule.every().thursday.at("17:00").do(Cac_master, cac)
#     schedule.every().friday.at("09:00").do(Cac_master, cac)
#     schedule.every().friday.at("17:00").do(Cac_master, cac)








    #loop to keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":
    main()

