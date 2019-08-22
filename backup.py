import datetime
from ib_insync import *
import pprint

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)



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
    print(trade.log)


def liquidatePosition(contract):
    position = getPosition(contract)
    quantity = position[2]
    placeMarketOrder(contract,'Sell', quantity )



def main():
    # create cac futures contracts

    #//////////////////////Prints list of all available cac futures
    # cac = Future('CAC40')
    # ib.qualifyContracts(cac)
    # print(cac)
    #//////////////////////

    #/////////  define contract ////////
    cac = Future(conId=372585961)
    #updates passed contract with full contract details
    ib.qualifyContracts(cac)

    #/////////  get position in current contract ////////
    # position = getPosition(cac)
    # print(position[2])


    #/////////  get price of contract ////////
    #price = getMarketPrice(cac)
    #print(price)

    #/////////  place trade ////////
    #'Buy' or 'Sell'
    #direction = 'Buy'
    #quantity = 4
    #placeMarketOrder(cac, direction, quantity)

    #/////////  liquidate position ////////
    liquidatePosition(cac)


    ib.disconnect()




if __name__ == "__main__":
    main()

