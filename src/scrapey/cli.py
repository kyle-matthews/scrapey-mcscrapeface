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
@click.option("--price",      type=float,  default=None, help="Price you're considering paying (£)")
@click.option("--pages",      type=int,    default=3, show_default=True, help="Sold-listing pages to scrape (~60 results each)")
@click.option("--sort", "sort_field", type=click.Choice(["price", "condition"]), default=None, help="Sort results by field")
@click.option("--desc",       is_flag=True, default=False, help="Reverse sort order (use with --sort)")
@click.option("--limit",      type=int,    default=None, help="Max rows to show in each table (stats use all results)")
@click.option("--exclude",    multiple=True, metavar="WORD", help="Exclude listings whose title contains WORD (repeatable)")
@click.option("--min-price",  type=float,  default=None, help="Exclude listings below this price")
@click.option("--max-price",  type=float,  default=None, help="Exclude listings above this price")
@click.option("--condition",  default=None, metavar="TEXT", help="Only include listings matching this condition (e.g. 'Pre-owned')")
@click.option("--compact",    is_flag=True, default=False, help="Show stats panel only — skip listing tables")
@click.option("--headless",   is_flag=True, default=False, help="Run browser in headless mode (no window)")
def main(
    search_term: str,
    price: float | None,
    pages: int,
    sort_field: str | None,
    desc: bool,
    limit: int | None,
    exclude: tuple[str, ...],
    min_price: float | None,
    max_price: float | None,
    condition: str | None,
    compact: bool,
    headless: bool,
) -> None:
    """Research sold prices on eBay UK for SEARCH_TERM."""

    def on_progress(msg: str) -> None:
        console.print(f"  [cyan]↳ {msg}…[/cyan]")

    console.print(f"\n[bold cyan]Scraping '{search_term}'[/bold cyan]")
    sold_pages, active_pages = scraper.scrape(search_term, pages, headed=not headless, on_progress=on_progress)
    console.print()

    if not sold_pages:
        console.print("[red]No pages fetched — check your connection or eBay login requirement.[/red]")
        sys.exit(1)

    try:
        listings = parser.parse_pages(sold_pages)
    except parser.NoResultsError:
        console.print(f'[yellow]No sold listings found for "[bold]{search_term}[/bold]". Try broadening your search.[/yellow]')
        sys.exit(0)

    if not listings:
        console.print(
            "[red]No listings parsed.[/red]\n"
            "eBay may have changed its markup or blocked the request."
        )
        sys.exit(1)

    listings = parser.filter_listings(listings, exclude, min_price, max_price, condition)

    if not listings:
        console.print("[yellow]No listings matched your filters.[/yellow]")
        sys.exit(0)

    prices  = [item["sold_price"] for item in listings]
    stats   = analytics.compute_stats(prices)
    display_listings = _sort(listings, sort_field, desc)
    if limit:
        display_listings = display_listings[:limit]

    display.show_stats(search_term, stats, display_listings, compact=compact)

    if not compact and active_pages:
        active_listings = parser.parse_active_pages(active_pages)
        active_listings = parser.filter_listings(active_listings, exclude, min_price, max_price, condition)
        active_listings = _sort(active_listings, sort_field, desc)
        if limit:
            active_listings = active_listings[:limit]
        if active_listings:
            display.show_active_listings(active_listings, stats["median"])

    if price is not None:
        label, colour = analytics.verdict(price, stats["median"])
        display.show_verdict(price, stats["median"], label, colour)
