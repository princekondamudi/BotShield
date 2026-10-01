# attack.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.goto("http://localhost:8000/test.html")
    page.fill("input[name=name]", "Bot")
    page.fill("input[name=email]", "bot@spam.com")
    page.click("button")
    page.wait_for_timeout(1500)
    b.close()