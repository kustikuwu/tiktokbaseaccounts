
import csv
import os
import json
import time
import sqlite3
import socket
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

DB_PATH = "db.sqlite3"
SESSIONS_DIR = "sessions"
ACCOUNTS_CSV = "accounts.csv"  # Формат: name,proxy

def ensure_dirs():
    os.makedirs(SESSIONS_DIR, exist_ok=True)

def load_csv():
    with open(ACCOUNTS_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        accounts = [row for row in reader if row.get("name")]
    return accounts

def save_to_db(name, session_path, proxy):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO accounts (name, session_path, proxy) VALUES (?, ?, ?)",
              (name, session_path, proxy))
    conn.commit()
    conn.close()

def check_proxy(proxy_url):
    if not proxy_url:
        return True
    try:
        proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlopen('http://www.google.com', timeout=5)
        return True
    except Exception:
        return False

def login_and_save(name, proxy):
    session_file = f"{SESSIONS_DIR}/session_{name}.json"

    if proxy and not check_proxy(proxy):
        print(f"❌ [{name}] Прокси недоступен: {proxy}")
        return

    print(f"🌐 [{name}] Запуск браузера для входа...")
    with sync_playwright() as p:
        launch_args = {"headless": False}
        if proxy:
            launch_args["proxy"] = {"server": proxy}

        browser = p.chromium.launch(**launch_args)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.tiktok.com/login", timeout=60000)

        input(f"🔐 [{name}] Войдите вручную, затем нажмите Enter...")

        cookies = context.cookies()
        with open(session_file, "w") as f:
            json.dump(cookies, f)

        browser.close()

    save_to_db(name, session_file, proxy)
    print(f"✅ [{name}] Сессия сохранена и добавлена в базу.")

def main():
    ensure_dirs()
    accounts = load_csv()
    print(f"🔄 Найдено аккаунтов: {len(accounts)}")

    for acc in accounts:
        name = acc["name"].strip()
        proxy = acc.get("proxy", "").strip()
        login_and_save(name, proxy)

if __name__ == "__main__":
    main()
