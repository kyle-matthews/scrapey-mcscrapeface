import sys
import click
from rich.console import Console

from scrapey import scraper, parser, analytics, display

console = Console()


@click.command()
@click.argument("search_term")
@click.option("--price", type=float, default=None, help="Price you're considering paying (£)")
@click.option("--pages", type=int, default=3, show_default=True, help="Number of pages to scrape (~60 results each)")
@click.option("--headed", is_flag=True, default=False, help="Open a visible browser window (useful if blocked)")
def main(search_term: str, price: float | None, pages: int, headed: bool) -> None:
    """Research sold prices on eBay UK for SEARCH_TERM."""
    with console.status(f"[cyan]Scraping {pages} page(s) for '{search_term}'…[/cyan]"):
        html_pages = scraper.scrape(search_term, pages, headed=headed)

    if not html_pages:
        console.print("[red]No pages fetched — check your connection or eBay login requirement.[/red]")
        sys.exit(1)

    listings = parser.parse_pages(html_pages)

    if not listings:
        console.print(
            "[red]No listings parsed.[/red]\n"
            "eBay may have changed its markup, blocked the request, or returned no results."
        )
        sys.exit(1)

    prices = [item["sold_price"] for item in listings]
    stats = analytics.compute_stats(prices)

    display.show_stats(search_term, stats, listings)

    if price is not None:
        label, colour = analytics.verdict(price, stats["median"])
        display.show_verdict(price, stats["median"], label, colour)
