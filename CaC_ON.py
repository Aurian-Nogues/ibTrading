import datetime
from ib_insync import *
import pprint
import schedule, time, sys

ib = IB()


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
    #for some reason paper account doesn't share sub with live so need to send request to live
    
    #disconnect from paper account and connect to live
    ib.disconnect()
    ib.connect('127.0.0.1', 7496, clientId=1)

    ib.reqMktData(contract, '', False, False)
    ticker=ib.ticker(contract)
    ib.sleep(2)

    #disconnect from live
    ib.disconnect()

    return ticker.marketPrice()


def placeMarketOrder(contract, direction, quantity):
    order = MarketOrder(direction, quantity)
    trade = ib.placeOrder(contract, order)
    ib.sleep(1)
    print('Market order placed:')
    print(trade.log)


def liquidatePosition(contract):
    position = getPosition(contract)
    quantity = position[2]
    placeMarketOrder(contract,'Sell', quantity )
    print('Liquidation order placed')

def createCacContract():
    #create contract for cac future expiring 20 sept 2019
    contract = Future(conId=372585961)
    ib.qualifyContracts(contract)
    return contract

def eveningOpen(contract):
    ib.connect('127.0.0.1', 7497, clientId=1)
    print('\n')
    position = getPosition(contract)
    if position is None:
        print('opening position...')
        direction = 'Buy'
        quantity = 1
        placeMarketOrder(contract, direction, quantity)
        ib.disconnect()

    else:
        print('Error, there already is a position open')
        print('liquidating position and stopping algo')
        liquidatePosition(contract)
        ib.disconnect()
        sys.exit()


def morningClose(contract):
    ib.connect('127.0.0.1', 7497, clientId=1)
    print('\n')
    print('Closing position...')
    position = getPosition(contract)
    if position is not None:
        liquidatePosition(contract)
        ib.disconnect()
    else:
        print('Error, there is no position to close')
        print('Algo is still running, will open position this evening')
        ib.disconnect()

def main():

    #define working contract
    ib.connect('127.0.0.1', 7497, clientId=1)
    cac = createCacContract()
    ib.disconnect()

    #////// tasks schedule //////
    schedule.every().thursday.at("15:28").do(eveningOpen, contract = cac)
    schedule.every().thursday.at("15:29").do(morningClose, contract = cac)
    schedule.every().thursday.at("15:31").do(eveningOpen, contract = cac)
    schedule.every().thursday.at("15:31").do(morningClose, contract = cac)

    #loop to keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":
    main()

