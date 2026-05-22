import sys
import click
from rich.console import Console

from scrapey import scraper, parser, analytics, display

console = Console()

SORT_KEYS = {
    "price":     (lambda x: x.get("sold_price") or x.get("price") or 0),
    "condition": (lambda x: x.get("condition", "").lower()),
}


def _sort(listings: list[dict], field: str | None, desc: bool) -> list[dict]:
    if field is None:
        return listings
    return sorted(listings, key=SORT_KEYS[field], reverse=desc)


@click.command()
@click.argument("search_term")
@click.option("--price", type=float, default=None, help="Price you're considering paying (£)")
@click.option("--pages", type=int, default=3, show_default=True, help="Number of sold-listing pages to scrape (~60 results each)")
@click.option("--sort", "sort_field", type=click.Choice(["price", "condition"]), default=None, help="Sort results by field")
@click.option("--desc", is_flag=True, default=False, help="Reverse sort order (use with --sort)")
@click.option("--headless", is_flag=True, default=False, help="Run browser in headless mode (no window)")
def main(search_term: str, price: float | None, pages: int, sort_field: str | None, desc: bool, headless: bool) -> None:
    """Research sold prices on eBay UK for SEARCH_TERM."""
    with console.status(f"[cyan]Scraping '{search_term}'…[/cyan]"):
        sold_pages, active_pages = scraper.scrape(search_term, pages, headed=not headless)

    if not sold_pages:
        console.print("[red]No pages fetched — check your connection or eBay login requirement.[/red]")
        sys.exit(1)

    listings = parser.parse_pages(sold_pages)

    if not listings:
        console.print(
            "[red]No listings parsed.[/red]\n"
            "eBay may have changed its markup, blocked the request, or returned no results."
        )
        sys.exit(1)

    prices = [item["sold_price"] for item in listings]
    stats = analytics.compute_stats(prices)

    display.show_stats(search_term, stats, _sort(listings, sort_field, desc))

    if active_pages:
        active_listings = parser.parse_active_pages(active_pages)
        if active_listings:
            display.show_active_listings(_sort(active_listings, sort_field, desc), stats["median"])

    if price is not None:
        label, colour = analytics.verdict(price, stats["median"])
        display.show_verdict(price, stats["median"], label, colour)
