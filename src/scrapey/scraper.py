import random
import sys
import time
import urllib.parse

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

BASE_URL = "https://www.ebay.co.uk/sch/i.html"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

_stealth = Stealth()


def scrape(search_term: str, pages: int, headed: bool = False) -> list[str]:
    html_pages = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="en-GB",
            viewport={"width": 1280, "height": 900},
            extra_http_headers={"Accept-Language": "en-GB,en;q=0.9"},
        )
        page = context.new_page()
        _stealth.apply_stealth_sync(page)

        for n in range(1, pages + 1):
            url = _build_url(search_term, n)
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)

            if "/signin" in page.url:
                print(
                    "[scraper] eBay requires login to view this data.\n"
                    "          Run with --headed to log in manually.",
                    file=sys.stderr,
                )
                break

            if "Access Denied" in page.title():
                print(
                    "[scraper] eBay blocked the request (Akamai WAF).\n"
                    "          This tool works on residential broadband.\n"
                    "          If you're on a VPN or corporate network, try disabling it.",
                    file=sys.stderr,
                )
                break

            html_pages.append(page.content())

            if n < pages:
                time.sleep(random.uniform(1.5, 3.5))

        browser.close()
    return html_pages


def _build_url(term: str, page: int) -> str:
    params = {
        "_nkw": term,
        "LH_Complete": "1",
        "LH_Sold": "1",
        "_pgn": str(page),
    }
    return f"{BASE_URL}?{urllib.parse.urlencode(params)}"
