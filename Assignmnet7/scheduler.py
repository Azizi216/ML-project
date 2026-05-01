import schedule
import time
from batch_predict import run_batch_prediction

schedule.every(5).minutes.do(run_batch_prediction)

print("🚀 Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(1)
