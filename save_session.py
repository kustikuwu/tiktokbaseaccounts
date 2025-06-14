
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.tiktok.com/login")
    input("Login manually, then press Enter to save session...")
    cookies = context.cookies()
    with open("sessions/session_1.json", "w") as f:
        json.dump(cookies, f)
    browser.close()
