import schedule, time, threading

def test1():
    print('tic')

def test2():
    print('toc')

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every(1).seconds.do(run_threaded, test1)
#schedule.every().thursday.at("14:52").do(run_threaded, job)




while True:
    schedule.run_pending()
    time.sleep(1)