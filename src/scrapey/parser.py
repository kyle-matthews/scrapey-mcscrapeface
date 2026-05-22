import re
import sys
from bs4 import BeautifulSoup


def parse_pages(html_pages: list[str]) -> list[dict]:
    listings = []
    for html in html_pages:
        listings.extend(_parse_page(html))
    return listings


def parse_active_pages(html_pages: list[str]) -> list[dict]:
    listings = []
    for html in html_pages:
        listings.extend(_parse_active_page(html))
    return listings


def _parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    items = soup.select("li.s-card")

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
    title_el    = item.select_one("span.su-styled-text.primary.default")
    price_el    = item.select_one("span.s-card__price")
    date_el     = item.select_one("div.s-card__caption span.su-styled-text")
    condition_el = item.select_one("div.s-card__subtitle")
    link_el     = item.select_one("a.s-card__link")

    if not title_el or not price_el:
        return None

    if title_el.get_text(strip=True).lower() == "shop on ebay":
        return None

    price_text = price_el.get_text(strip=True)

    # skip multi-lot range prices like "£5.00 to £15.00"
    if " to " in price_text.lower():
        return None

    price = _parse_price(price_text)
    if price is None:
        return None

    condition = ""
    if condition_el:
        # subtitle is e.g. "Parts only ·Lenovo" — take the part before " ·"
        raw = condition_el.get_text(strip=True)
        condition = raw.split(" ·")[0].strip()

    return {
        "title": title_el.get_text(strip=True),
        "sold_price": price,
        "date_sold": date_el.get_text(strip=True) if date_el else "",
        "condition": condition,
        "url": link_el["href"] if link_el else "",
    }


def _parse_active_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    items = soup.select("li.s-card")
    results = []
    for item in items:
        listing = _extract_active(item)
        if listing:
            results.append(listing)
    return results


def _extract_active(item) -> dict | None:
    title_el   = item.select_one("span.su-styled-text.primary.default")
    price_el   = item.select_one("span.s-card__price")
    link_el    = item.select_one("a.s-card__link")
    type_el    = item.select_one("span.su-styled-text.primary.bold.large")
    subtitles  = item.select("div.s-card__subtitle")

    if not title_el or not price_el:
        return None

    if title_el.get_text(strip=True).lower() == "shop on ebay":
        return None

    price_text = price_el.get_text(strip=True)
    if " to " in price_text.lower():
        return None

    price = _parse_price(price_text)
    if price is None:
        return None

    # condition is in the last subtitle, formatted "Pre-owned ·Brand"
    condition = ""
    if subtitles:
        raw = subtitles[-1].get_text(strip=True)
        condition = raw.split(" ·")[0].strip()

    listing_type = type_el.get_text(strip=True) if type_el else "Auction"

    return {
        "title": title_el.get_text(strip=True),
        "price": price,
        "listing_type": listing_type,
        "condition": condition,
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
