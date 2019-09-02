import datetime
import schedule, time




def test(arg1, arg2):
    print(arg1)
    print(arg2)


arg1 = "tic"
arg2 = "toc"

schedule.every(2).seconds.do(test, arg1, arg2)

#schedule.every().monday.at("09:00").do(futArb, contracts)


#loop to keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(1)
