import re
import sys
from bs4 import BeautifulSoup


def parse_pages(html_pages: list[str]) -> list[dict]:
    listings = []
    for html in html_pages:
        listings.extend(_parse_page(html))
    return listings


def _parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    items = soup.select("li.s-item")

    if not items:
        print("[parser] warning: no listing elements found — eBay markup may have changed", file=sys.stderr)
        return []

    results = []
    for item in items:
        listing = _extract(item)
        if listing:
            results.append(listing)
    return results


def _extract(item) -> dict | None:
    title_el = item.select_one(".s-item__title")
    price_el = item.select_one(".s-item__price")
    date_el = item.select_one(".s-item__ended-date") or item.select_one(".s-item__listingDate")
    condition_el = item.select_one(".SECONDARY_INFO")
    link_el = item.select_one("a.s-item__link")

    if not title_el or not price_el:
        return None

    title = title_el.get_text(strip=True)
    if title.lower() == "shop on ebay":
        return None

    price_text = price_el.get_text(strip=True)

    # skip multi-lot range prices like "£5.00 to £15.00"
    if " to " in price_text.lower():
        return None

    price = _parse_price(price_text)
    if price is None:
        return None

    return {
        "title": title,
        "sold_price": price,
        "date_sold": date_el.get_text(strip=True) if date_el else "",
        "condition": condition_el.get_text(strip=True) if condition_el else "",
        "url": link_el["href"] if link_el else "",
    }


def _parse_price(text: str) -> float | None:
    match = re.search(r"[\d,]+\.?\d*", text.replace("£", "").replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None
