
import sqlite3
import json
import random
import time
import threading
from playwright.sync_api import sync_playwright

DB_PATH = "db.sqlite3"
MAX_THREADS = 3

def execute_command(command):
    command_id, account_id, action, url, _ = command
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("SELECT session_path FROM accounts WHERE id = ?", (account_id,))
        session_path = c.fetchone()[0]

        with open(session_path, 'r') as f:
            cookies = json.load(f)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(user_agent=random_user_agent())
            context.add_cookies(cookies)
            page = context.new_page()
            page.goto(url, timeout=60000)
            time.sleep(random.uniform(4, 6))  # "естественная" задержка

            if action == "like":
                page.locator('xpath=//button[contains(@aria-label, "like")]').click()
                print("Liked video.")
            elif action == "follow":
                page.locator('xpath=//button[contains(text(), "Follow")]').click()
                print("Followed user.")
            elif action == "view":
                print("Viewing video...")
                time.sleep(random.uniform(10, 20))
                print("Viewed video.")

            c.execute("UPDATE commands SET status = 'done' WHERE id = ?", (command_id,))
            conn.commit()
            browser.close()

    except Exception as e:
        print(f"Error processing command {command_id}: {e}")
        c.execute("UPDATE commands SET status = 'failed' WHERE id = ?", (command_id,))
        conn.commit()

    finally:
        conn.close()

def worker():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM commands WHERE status = 'pending' LIMIT 1")
    command = c.fetchone()
    conn.close()

    if command:
        execute_command(command)

def run_bot():
    threads = []
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
        time.sleep(1)

    for t in threads:
        t.join()

def random_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
