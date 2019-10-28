
import datetime, time
from ib_insync import *
import schedule, time, sys
import csv
import re
import math


ib = IB()

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

def jb_CreateContract():
    checkConnection()
    #create contract for Japanese Bond expirint 13/12/2019
    contract = Future(localSymbol="164120001", exchange = "OSE.JPN")
    #ib.reqContractDetails(contract)
    try:
        ib.qualifyContracts(contract)
    except :
        time.sleep(5)
        checkConnection()
        ib.qualifyContracts(contract)
    return contract

def getMarketPrice(contract):
    checkConnection()
    #change this to change type of market data
    ib.reqMarketDataType(1) #1=live / 2= frozen / 3=delayed / 4=delayed frozen
 
    

    ib.reqMktData(contract, '', False, False)
    ticker=ib.ticker(contract)
    ib.sleep(2)

    return ticker.marketPrice()

def Cac_CreateContract():
    checkConnection()
    #create contract for cac future expiring 20 sept 2019
    contract = Future(localSymbol="MFCX9", exchange = "MONEP")
    #ib.reqContractDetails(contract)
    try:
        ib.qualifyContracts(contract)
    except :
        time.sleep(5)
        checkConnection()
        ib.qualifyContracts(contract)
    return contract

def getJbReferencePrice():

    today = datetime.datetime.today()
    weekday = today.weekday() #returns integer, monday=0, tuesday=1...
    
    if weekday > 5: #if today is monday to friday
        return

    global jbContract
    global jbRefPrice
    
    checkConnection()
    
    jbContract = jb_CreateContract()
    jbRefPrice = getMarketPrice(jbContract)
    print('/////')
    print(type(jbRefPrice))
    print(jbRefPrice)
    print('/////')
    while True:
        if math.isnan(jbRefPrice):
            ib.sleep(5)
            print("Could not recover jb price, trying again")
            checkConnection()
            jbRefPrice = getMarketPrice(jbContract)
        else:
            print("Successfully got JB price : " + str(jbRefPrice))
            break

    print('Started JB, reference price is ' + str(jbRefPrice))
    



contract = Cac_CreateContract()

print(contract)