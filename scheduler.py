# scheduler.py
import threading
import time
from bot import run_bot

def schedule_run(interval=30):
    def job():
        while True:
            print("⏳ Проверка команд...")
            run_bot()
            time.sleep(interval)

    thread = threading.Thread(target=job, daemon=True)
    thread.start()
