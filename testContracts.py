import datetime, time
from ib_insync import *
import schedule, time, sys
import csv
import re



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


#//////// contracts /////////
def Cac_CreateContract():
    checkConnection()
    #create contract for cac future expiring 20 sept 2019
    contract = Future(localSymbol="MFCV9", exchange = "MONEP")
    #ib.reqContractDetails(contract)
    try:
        ib.qualifyContracts(contract)
    except :
        time.sleep(5)
        checkConnection()
        ib.qualifyContracts(contract)
    return contract

def Es_CreateContract():
    checkConnection()
    #create contract for S&P500 mini future expiring 20 sept 2019
    contract = Future(localSymbol="ESZ9", exchange = "GLOBEX")
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
    contract = Future(localSymbol="RTYZ9", exchange = "GLOBEX")
    #ib.reqContractDetails(contract)
    ib.qualifyContracts(contract)
    return contract


cac = Cac_CreateContract()
print(cac)

es = Es_CreateContract()
print(es)

nq = Nasdaq_CreateContract()
print(nq)

rs = Russel_CreateContract()
print(rs)
