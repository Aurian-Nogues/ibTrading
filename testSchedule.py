import schedule, time, threading


def job():
    print('tic')

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every(1).seconds.do(run_threaded, job)
#schedule.every().thursday.at("13:51").do(job)




while True:
    schedule.run_pending()
    time.sleep(1)