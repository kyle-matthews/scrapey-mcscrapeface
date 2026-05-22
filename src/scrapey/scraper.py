import json
import random
import shutil
import sys
import time
import urllib.parse
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

BASE_URL = "https://www.ebay.co.uk/sch/i.html"
HOME_URL = "https://www.ebay.co.uk"
COOKIE_FILE = Path.home() / ".scrapey" / "cookies.json"
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

        _load_cookies(context)

        page = context.new_page()
        _stealth.apply_stealth_sync(page)

        # Visit homepage first to warm up the session
        page.goto(HOME_URL, wait_until="load", timeout=30_000)
        time.sleep(random.uniform(1.0, 2.0))

        for n in range(1, pages + 1):
            url = _build_url(search_term, n)
            page.goto(url, wait_until="load", timeout=45_000)

            title = page.title()

            if "/signin" in page.url:
                print(
                    "[scraper] eBay requires login to view this data.\n"
                    "          Run with --headed to log in manually.",
                    file=sys.stderr,
                )
                break

            if "Access Denied" in title:
                print(
                    "[scraper] eBay blocked the request.\n"
                    "          Try running with --headed for a visible browser window.",
                    file=sys.stderr,
                )
                break

            if "Pardon our interruption" in title:
                if headed:
                    print(
                        "[scraper] eBay CAPTCHA detected — solve it in the browser window.",
                        file=sys.stderr,
                    )
                    # Wait for the user to solve it and land on a real page
                    try:
                        page.wait_for_function(
                            "!document.title.includes('Pardon our interruption')",
                            timeout=120_000,
                        )
                        _save_cookies(context)
                        # Re-navigate to where we actually wanted to go
                        page.goto(url, wait_until="load", timeout=45_000)
                    except Exception:
                        print("[scraper] Timed out waiting for CAPTCHA solve.", file=sys.stderr)
                        break
                else:
                    print(
                        "[scraper] eBay CAPTCHA challenge — run with --headed to solve it once:\n"
                        "          scrapey \"" + search_term + "\" --headed\n"
                        "          Your session will be saved for future headless runs.",
                        file=sys.stderr,
                    )
                    break

            html_pages.append(page.content())
            _save_cookies(context)

            if n < pages:
                time.sleep(random.uniform(2.0, 4.0))

        browser.close()
    return html_pages


def _launch(p, headed: bool):
    chrome = shutil.which("google-chrome") or shutil.which("google-chrome-stable")
    if chrome:
        try:
            return p.chromium.launch(headless=not headed, channel="chrome")
        except Exception:
            pass
    return p.chromium.launch(headless=not headed)


def _save_cookies(context) -> None:
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    COOKIE_FILE.write_text(json.dumps(context.cookies()))


def _load_cookies(context) -> None:
    if COOKIE_FILE.exists():
        try:
            context.add_cookies(json.loads(COOKIE_FILE.read_text()))
        except Exception:
            COOKIE_FILE.unlink(missing_ok=True)


def _build_url(term: str, page: int) -> str:
    params = {
        "_nkw": term,
        "LH_Complete": "1",
        "LH_Sold": "1",
        "_pgn": str(page),
    }
    return f"{BASE_URL}?{urllib.parse.urlencode(params)}"
