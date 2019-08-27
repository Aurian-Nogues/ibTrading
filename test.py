from ib_insync import *
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)
print(ib.isConnected())