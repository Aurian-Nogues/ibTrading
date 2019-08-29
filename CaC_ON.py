import datetime
from ib_insync import *
import pprint
import schedule, time, sys
import csv
import re


ib = IB()

#define global variables
cacOnState = ''


#//////// contracts /////////

def createCacContract():
    #create contract for cac future expiring 20 sept 2019
    contract = Future(conId=372585961)
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


def eveningOpen(contract):
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


def morningClose(contract):
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


def masterCacOn(contract):
    #This functions determines wether to open or close a trade in CAC_ON

    global cacOnState

    if cacOnState == 'Closed':
            eveningOpen(contract)
            cacOnState = 'Open'
    elif cacOnState == 'Open':
            morningClose(contract)
            cacOnState = 'Closed'



#//////////// app ///////////////////////


def main():

    #Start CAC_on strategy

    checkConnection()

    cac = createCacContract()
    positionCac = getPosition(cac)
   
    global cacOnState
    if positionCac is None:
        cacOnState = 'Closed'
    else:
        cacOnState = 'Open'

    #schedule.every(5).seconds.do(masterCacOn, cac)


    schedule.every().monday.at("09:00").do(masterCacOn, cac)
    schedule.every().monday.at("17:00").do(masterCacOn, cac)
    schedule.every().tuesday.at("09:00").do(masterCacOn, cac)
    schedule.every().tuesday.at("17:00").do(masterCacOn, cac)
    schedule.every().wednesday.at("09:00").do(masterCacOn, cac)
    schedule.every().wednesday.at("17:00").do(masterCacOn, cac)
    schedule.every().thursday.at("09:00").do(masterCacOn, cac)
    schedule.every().thursday.at("17:00").do(masterCacOn, cac)
    schedule.every().friday.at("09:00").do(masterCacOn, cac)
    schedule.every().friday.at("17:00").do(masterCacOn, cac)


    #loop to keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":
    main()

