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

def main():

    # create cac futures contracts

    #//////////////////////Prints list of all available cac futures
    # cac = Future('CAC40')
    # ib.qualifyContracts(cac)
    # print(cac)
    #//////////////////////

    #define contract

    cac = Future(conId=372585961)
    #updates passed contract with full contract details
    ib.qualifyContracts(cac)

    #/////////  get position in current contract ////////
    # position = getPosition(cac)
    # print(position[2])


    #/////////  get price of contract ////////
    # price = getMarketPrice(cac)
    # print(price)

    


    ib.disconnect()

    # #get market price
    # ib.reqMktData(cac, '', False, False)
    # ticker=ib.ticker(cac)
    # ib.sleep(2)
    # print(ticker.marketPrice())

    # #place an order
    # order = MarketOrder('Buy', 1)
    # trade = ib.placeOrder(cac, order)

    # ib.sleep(1)
    # print(trade.log)

    #check positions and select relevant contract


if __name__ == "__main__":
    main()






# # get the index tickers and subscribe to live tick data
# vixTicker, vxnTicker = ib.reqTickers(vix, vxn)
# ib.reqMktData(vix, '', False, False)
# ib.reqMktData(vxn, '', False, False)

# # loop that runs until the market conditions are met
# while ib.waitOnUpdate():
#     if vixTicker.marketPrice() - vxnTicker.marketPrice() >= 10:
#         print('VIX has popped')
#         break

# # do other stuff here