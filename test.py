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

def placeMarketOrder(contract, direction, quantity, strategy):
    order = MarketOrder(direction, quantity)
    trade = ib.placeOrder(contract, order)
    ib.sleep(1)
    print('Market order placed, strategy is ' + str(strategy))
    tradeLog = trade.log





def Cac_CreateContract():
    #create contract for cac future expiring 20 sept 2019
    contract = Future(localSymbol="MFCU9", exchange = "MONEP")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract

def Es_CreateContract():
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



def futArbInitial():
    checkConnection()

    today = datetime.datetime.today()
    weekday = today.weekday() #returns integer, monday=0, tuesday=1...
    
    if weekday <= 5: #if today is monday to friday
        global futArb_state
        futArb_state = 'closed'

        russel = Russel_CreateContract()
        es = Es_CreateContract()
        contracts = [russel, es]

        prices = getMultipleMarketPrices(contracts)
        russelPrice = prices[0]
        esPrice = prices[1]
        initComboPrice = esPrice - 2*russelPrice

        return initComboPrice, contracts

def futArbMonitor(initComboPrice, contracts):
    checkConnection()
    global futArb_state

    #tests
    #futArb_state = 'open'

    if futArb_state == 'non_triggerable': #strategy non triggerable because already closed
        print('futarb is not triggerable')

    elif futArb_state == 'closed': #check if we should be opening a position

        prices = getMultipleMarketPrices(contracts)
        russelPrice = prices[0]
        esPrice = prices[1]
        currentComboPrice = esPrice - 2*russelPrice

        lowBoudary = initComboPrice -250
        highBoundary = initComboPrice + 250

        #tests
        #currentComboPrice = initComboPrice -300

        if currentComboPrice <= lowBoudary:
            print('-1ES +2RTY')
            futArb_state = 'open'
        if currentComboPrice >= highBoundary:
            print('+1ES -2RTY')
            futArb_state = 'open'

    elif futArb_state == 'open':

        prices = getMultipleMarketPrices(contracts)
        russelPrice = prices[0]
        esPrice = prices[1]
        currentComboPrice = esPrice - 2*russelPrice

        
        lowBoudary = initComboPrice -500 -250 #cut position if P&L is > 500
        highBoundary = initComboPrice + 500 + 250 #cut position if P&L is > 500
        #tests
        #currentComboPrice = initComboPrice +400

        if currentComboPrice <= lowBoudary:
            print('close position')
            futArb_state = 'non_triggerable'
        if currentComboPrice >= highBoundary:
            print('close position')
            futArb_state = 'non_triggerable'

def liquidatePosition(contract, strategy):
    checkConnection()
    position = getPosition(contract)
    quantity = position[2]
    placeMarketOrder(contract,'Sell', quantity, strategy )
    print('Liquidation order placed')


def futArbClose(contracts):
    checkConnection()
    global futArb_state
    if futArb_state == 'open':
        #get contracts
        russel = contracts[0]
        es = contracts[1]

        

        #close es
        position = getPosition(es)[2]
        if position > 0:
            direction  = 'Sell'
        if position < 0:
            direction = 'Buy'
        
        quantity = abs(position)


        placeMarketOrder(es, direction, quantity, strategy)








checkConnection()

futArb_state = 'open'


russel = Russel_CreateContract()
es = Es_CreateContract()
contracts = [russel, es]

#open position 


#placeMarketOrder(es, 'sell', 1, 'futArb')
futArbClose(contracts)

        


        
    





#initComboPrice, contracts = futArbInitial()
#futArbMonitor(initComboPrice, contracts)





#russelPrice = getMarketPrice([russel, nasdaq])
#nasdaqPrice = getMarketPrice(nasdaq)
#sePrice = getMarketPrice(se)

#print(russelPrice)
#print(nasdaqPrice)
#print(sePrice)



