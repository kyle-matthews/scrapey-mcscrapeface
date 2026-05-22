import random
import shutil
import sys
import time
import urllib.parse

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

BASE_URL = "https://www.ebay.co.uk/sch/i.html"
HOME_URL = "https://www.ebay.co.uk"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

_stealth = Stealth()


def scrape(search_term: str, pages: int, headed: bool = False) -> list[str]:
    html_pages = []
    with sync_playwright() as p:
        browser = _launch(p, headed)
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="en-GB",
            viewport={"width": 1280, "height": 900},
            extra_http_headers={
                "Accept-Language": "en-GB,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            },
        )
        page = context.new_page()
        _stealth.apply_stealth_sync(page)

        # Visit homepage first to establish a real session and pick up cookies
        page.goto(HOME_URL, wait_until="load", timeout=30_000)
        time.sleep(random.uniform(1.0, 2.0))

        for n in range(1, pages + 1):
            url = _build_url(search_term, n)
            page.goto(url, wait_until="load", timeout=45_000)

            if "/signin" in page.url:
                print(
                    "[scraper] eBay requires login to view this data.\n"
                    "          Run with --headed to log in manually.",
                    file=sys.stderr,
                )
                break

            if "Access Denied" in page.title():
                print(
                    "[scraper] eBay blocked the request.\n"
                    "          Try running with --headed for a visible browser window.",
                    file=sys.stderr,
                )
                break

            html_pages.append(page.content())

            if n < pages:
                time.sleep(random.uniform(2.0, 4.0))

        browser.close()
    return html_pages


def _launch(p, headed: bool):
    # Prefer real installed Chrome — it has a genuine TLS fingerprint Akamai trusts
    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if chrome:
        try:
            return p.chromium.launch(headless=not headed, channel="chrome")
        except Exception:
            pass
    return p.chromium.launch(headless=not headed)


def _build_url(term: str, page: int) -> str:
    params = {
        "_nkw": term,
        "LH_Complete": "1",
        "LH_Sold": "1",
        "_pgn": str(page),
    }
    return f"{BASE_URL}?{urllib.parse.urlencode(params)}"
