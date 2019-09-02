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


#//////////////////////////////


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
        


def getPosition(contract):
    checkConnection()
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
    checkConnection()
    #get market price of a contract
 
    

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
    checkConnection()
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

                if strategy == 'CAC_ON':
                    with open('CAC_ON_trading_log.csv', 'a') as f:
                            writer = csv.writer(f, lineterminator = '\n')
                            writer.writerow(logEntry)
                elif strategy == 'FutArb':
                    with open('FutArb_trading_log.csv', 'a') as f:
                            writer = csv.writer(f, lineterminator = '\n')
                            writer.writerow(logEntry)


def liquidatePosition(contract, strategy):
    checkConnection()
    position = getPosition(contract)
    quantity = position[2]
    if quantity >0:
        direction = "Sell"
    elif quantity < 0:
        direction = "Buy"
        quantity = abs(quantity)


    placeMarketOrder(contract,direction, quantity, strategy )
    print(str(strategy) + ', ' + str(contract) + ', ''Liquidation order placed')


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
    checkConnection()
    #This functions determines wether to open or close a trade in CAC_ON

    global cacOn_State

    if cacOn_State == 'Closed':
            Cac_eveningOpen(contract)
            cacOn_State = 'Open'
    elif cacOn_State == 'Open':
            Cac_morningClose(contract)
            cacOn_State = 'Closed'


def futArbInitial(contracts):
    checkConnection()
    global initComboPrice
    global futArb_state

    today = datetime.datetime.today()
    weekday = today.weekday() #returns integer, monday=0, tuesday=1...
    
    if weekday <= 5: #if today is monday to friday
        
        
        futArb_state = 'closed'
        print("Triggered futArb")

        prices = getMultipleMarketPrices(contracts)
        russelPrice = prices[0]
        esPrice = prices[1]
        initComboPrice = esPrice - 2*russelPrice
        

        

def futArbMonitor(contracts):
    checkConnection()
    global futArb_state
    global initComboPrice

    russel = contracts[0]
    es = contracts[1]

    #tests---------------------------------------
    #futArb_state = 'open'
    #-------------------------------------------

    if futArb_state == 'non_triggerable': #strategy non triggerable because already closed
        print('futarb is not triggerable')
        print('either we did not go through futArbInitial or P&L is <> $500')

    elif futArb_state == 'closed': #check if we should be opening a position

        prices = getMultipleMarketPrices(contracts)
        russelPrice = prices[0]
        esPrice = prices[1]
        currentComboPrice = esPrice - 2*russelPrice

        lowBoudary = initComboPrice -250
        highBoundary = initComboPrice + 250

        #tests---------------------------------------
        #currentComboPrice = initComboPrice -300
        #-------------------------------------------

        if currentComboPrice <= lowBoudary:
            print('futArb: opening position -1ES +2RTY')
            placeMarketOrder(es, "Sell", 1, 'FutArb')
            placeMarketOrder(russel, "Buy", 2, 'FutArb')
            futArb_state = 'open'

        if currentComboPrice >= highBoundary:
            print('futArb: opening position +1ES -2RTY')
            placeMarketOrder(es, "Buy", 1, 'FutArb')
            placeMarketOrder(russel, "Sell", 2, 'FutArb')
            futArb_state = 'open'

    elif futArb_state == 'open': #check if p$L is <> $500 so we should close

        prices = getMultipleMarketPrices(contracts)
        russelPrice = prices[0]
        esPrice = prices[1]
        currentComboPrice = esPrice - 2*russelPrice

        
        lowBoudary = initComboPrice -500 -250 #cut position if P&L is > 500
        highBoundary = initComboPrice + 500 + 250 #cut position if P&L is > 500
        #tests---------------------------------------
        #currentComboPrice = initComboPrice -800
        #-------------------------------------------

        if currentComboPrice <= lowBoudary:
            print('FutArb reached low boundary, closing position...')
            liquidatePosition(es, 'FutArb')
            liquidatePosition(russel, 'FutArb')
            futArb_state = 'non_triggerable'


        if currentComboPrice >= highBoundary:
            print('FutArb reached high boundary, closing position...')
            liquidatePosition(es, 'FutArb')
            liquidatePosition(russel, 'FutArb')
            futArb_state = 'non_triggerable'            


def futArbTimingClose(contracts):
    checkConnection()
    global futArb_state
    russel = contracts[0]
    es = contracts[1]

    if futArb_state == 'open':
        print('FutArb timing over, liquidating positions')
        liquidatePosition(es, 'FutArb')
        liquidatePosition(russel, 'FutArb')
        futArb_state = 'non_triggerable'
    elif futArb_state == 'closed':
        print("Futarb time window closed without opening position")
        futArb_state = 'non_triggerable'

    

def test():
    print("working")


#//////////// app ///////////////////////


def main():
    checkConnection()

#-------Start CAC_on strategy--------
#open position at 17:35 paris time, close it next day at 08:59 paris time


    cac = Cac_CreateContract()
    positionCac = getPosition(cac)
   
    global cacOn_State
    if positionCac is None:
        cacOn_State = 'Closed'
    else:
        cacOn_State = 'Open'



    #schedule.every(5).seconds.do(Cac_master, cac)
    #schedule.every().friday.at("12:40").do(Cac_master, cac)

#     schedule.every().monday.at("08:59").do(Cac_master, cac)
#     schedule.every().monday.at("17:35").do(Cac_master, cac)
#     schedule.every().tuesday.at("08:59").do(Cac_master, cac)
#     schedule.every().tuesday.at("17:35").do(Cac_master, cac)
#     schedule.every().wednesday.at("08:59").do(Cac_master, cac)
#     schedule.every().wednesday.at("17:35").do(Cac_master, cac)
#     schedule.every().thursday.at("08:59").do(Cac_master, cac)
#     schedule.every().thursday.at("17:35").do(Cac_master, cac)
#     schedule.every().friday.at("08:59").do(Cac_master, cac)
#     schedule.every().friday.at("17:35").do(Cac_master, cac)

#-------Start futArb strategy--------
#at 15:00 Paris time check the spread
#if spread deviates by +/- $250 in the next hour open a position
#if P&L is +/- $500 close position
#if after 1 hour position is still open, close it


    global futArb_state
    global initComboPrice
    futArb_state = 'non_triggerable'
    initComboPrice = None

    russel = Russel_CreateContract()
    es = Es_CreateContract()
    contractsFutArb = [russel, es]
    
    

    schedule.every().day.at("15:00").do(futArbInitial, contractsFutArb)

    schedule.every().day.at("15:02").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:04").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:06").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:08").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:10").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:12").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:14").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:16").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:18").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:20").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:22").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:24").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:26").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:28").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:30").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:32").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:34").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:36").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:38").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:40").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:42").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:44").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:46").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:48").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:50").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:52").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:54").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:56").do(futArbMonitor, contractsFutArb)
    schedule.every().day.at("15:58").do(futArbMonitor, contractsFutArb)

    schedule.every().day.at("16:00").do(futArbTimingClose, contractsFutArb)

    #schedule.every().monday.at("21:17").do(test)
    #schedule.every(2).seconds.do(test)



    #loop to keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":
    main()

