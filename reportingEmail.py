import configparser
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import datetime, time
import re

def buildFutarbPnl(date):
#Create trade recap and P&L

    log = pd.read_csv("FutArb_trading_log.csv", sep=',')
    futarb_report = None

    for row in log.iterrows():
        logDate = row[1]['Time']
        match = re.search(r'\d{4}-\d{2}-\d{2}', logDate)
        logDate = match.group()

        if logDate == date:
            #create table entries
            contract = row[1]['Contract']
            direction = row[1]['Direction']
            quantity = row[1]['Quantity']
            price = row[1]['Exec price']
            if direction == 'Buy':
                cashFlow = -1 * price * quantity * 50
            else:
                cashFlow = 1 * price * quantity * 50

            #create list if it doesn't exist yet
            if futarb_report == None:
                futarb_report = [[contract, direction, quantity, price, cashFlow]]
            else:
                futarb_report.append([contract, direction, quantity, price, cashFlow])

    #create dataframe
    futarb_dataframe = pd.DataFrame(futarb_report, columns = ['contract', 'direction', 'quantity', 'price', 'cashFlow'])


    futarb_pnl = 0
    for row in futarb_dataframe.iterrows():
        futarb_pnl += row[1]['cashFlow']
    
    if futarb_dataframe.empty == True:
        futarb_triggered = False
    else:
        futarb_triggered = True
        
    return futarb_dataframe, futarb_pnl, futarb_triggered


def buildFutarbHistoricalPnl():
#build historical PnL

    log = pd.read_csv("FutArb_trading_log.csv", sep=',')


    historicalReport = None
    buildingDate = None

    for row in log.iterrows():


        logDate = row[1]['Time']
        
        match = re.search(r'\d{4}-\d{2}-\d{2}', logDate)
        logDate = match.group()

        if logDate != buildingDate:
            buildingDate = logDate
            trades, pnl, _ = buildFutarbPnl(logDate)

            if historicalReport == None:
                historicalReport = [[logDate, pnl]]
            else:
                historicalReport.append([logDate, pnl])
    
    futarbHistoricalDataframe = pd.DataFrame(historicalReport, columns = ['Date', 'P&L'])
    return futarbHistoricalDataframe


def calculateMetrics(pnl):
    entries = pnl['P&L']
    averageReturn = pnl['P&L'].mean()
    totalReturn = pnl['P&L'].sum()
    entries = 0
    positives = 0
    
    for row in pnl.iterrows():
        value = row[1]['P&L']
        entries += 1
        if value > 0:
            positives +=1

    hitRatio = positives / entries
    
        
    
    
    return averageReturn, totalReturn, hitRatio

def futarbCreateReportContent():
    
    today = datetime.datetime.today()
    dateToday = today.strftime("%Y-%m-%d")

    historicalPnL = buildFutarbHistoricalPnl()
    averageReturn, totalReturn, hitRatio = calculateMetrics (historicalPnL)
    
    #format all variables for email
    averageReturn="{:.{}f}".format( averageReturn, 2 )
    totalReturn = "{:.{}f}".format( totalReturn, 2 )
    hitRatio = '{percent:.2%}'.format(percent=hitRatio)
    historicalPnL = str(historicalPnL.to_html(index=False))


    
    #========== test ===========
    #date = '2019-10-16' # need to replace with today date when in production
    #dailyTrades, dailyPNL, dailyTrigger = buildFutarbPnl(date)
    #========== test ===========
    dailyTrades, dailyPNL, dailyTrigger = buildFutarbPnl(dateToday)
    
    #format all variables for email
    dailyPNL = "{:.{}f}".format( dailyPNL, 2 )
    dailyTrades=str(dailyTrades.to_html(index=False))

    #print(dailyTrades)
    #print('P&L today: ' + str(dailyPNL))

    contents = {
        "dateToday" : dateToday,
        "averageReturn" : averageReturn,
        "totalReturn" : totalReturn,
        "hitRatio" : hitRatio,
        "historicalPnL" : historicalPnL,
        "dailyTrades" : dailyTrades,
        "dailyPNL" : dailyPNL,
        "dailyTrigger" : dailyTrigger
        
    }
    
    return contents

def emailConfiguration():
    config = configparser.ConfigParser()
    config.read("credentials.txt")

    email = config.get("credentials", "name")
    password = config.get("credentials","password")
    receiver_emails = config.get("credentials","receivers").split(",")
    
    return email, password, receiver_emails

def sendEmail(email, password, receiver_emails, futarbContents):

    port = 465  # For SSL
    
    #figure out what was triggered and build message accordingly
    dailyTrigger = futarbContents["dailyTrigger"]

    if dailyTrigger == True:
        futarbDailyMessage = "P&L today : " + str(futarbContents["dailyPNL"]) + "<br> Trades implemented: " + str(futarbContents["dailyTrades"]) + "<br>"
    else:
        futarbDailyMessage = "S&P vs Russel did not get triggered today"
    
    
    
    for receiver_email in receiver_emails:

        sender_email = email

        message = MIMEMultipart("alternative")
        message["Subject"] = "Trading report " + str(futarbContents["dateToday"]) 
        message["From"] = sender_email
        message["To"] = receiver_email

        #build body of message
        text = """\
        You need to enable HTML to read this message."""

        html = """\
        <html>
          <body>
            <p>
                <b>S&P vs Russel futures {dateToday}</b><br>
                {futarbDailyMessage}<br>
                
               <b>Historical P&L and performance</b><br>
               Average return: {futarbAverageReturn}<br>
               Total return: {futarbTotalReturn}<br>
               Hit Ratio: {futarbHitRatio}<br>
               <br>
               P&L since inception:<br>
               {futarbHistoricalPnL}

            </p>
          </body>
        </html>
        """.format(dateToday=futarbContents["dateToday"],futarbAverageReturn=futarbContents["averageReturn"],
                  futarbTotalReturn=futarbContents["totalReturn"],futarbHitRatio=futarbContents["hitRatio"],futarbHistoricalPnL=futarbContents["historicalPnL"],
                   futarbDailyMessage = futarbDailyMessage
                  )

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        return

def sendDailyReport():
    today = datetime.datetime.today()
    weekday = today.weekday() #returns integer, monday=0, tuesday=1...
    
    if weekday > 5: #if today is monday to friday
        return

    email, password, receiver_emails = emailConfiguration()
    futarbContents = futarbCreateReportContent()
    sendEmail(email, password, receiver_emails, futarbContents)
    print("Sent reporting email")