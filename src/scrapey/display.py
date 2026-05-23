from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from scrapey.analytics import GOOD_DEAL_THRESHOLD, OVERPRICED_THRESHOLD

console = Console()


def _price_colour(price: float, median: float) -> str:
    ratio = price / median
    if ratio < GOOD_DEAL_THRESHOLD:
        return "green"
    if ratio <= OVERPRICED_THRESHOLD:
        return "yellow"
    return "red"


def show_stats(term: str, stats: dict, listings: list[dict], compact: bool = False) -> None:
    summary = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    summary.add_column("Metric", style="dim")
    summary.add_column("Value", style="bold")

    summary.add_row("Median", f"£{stats['median']:.2f}")
    summary.add_row("Mean",   f"£{stats['mean']:.2f}")
    summary.add_row("Low",    f"£{stats['low']:.2f}")
    summary.add_row("High",   f"£{stats['high']:.2f}")
    summary.add_row("Std Dev",f"£{stats['std_dev']:.2f}")
    summary.add_row("Results",str(stats["count"]))

    console.print(Panel(summary, title=f"[bold cyan]{term}[/bold cyan] — sold prices", border_style="cyan"))

    if compact:
        return

    median = stats["median"]
    listings_table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold dim")
    listings_table.add_column("Price", no_wrap=True, width=10)
    listings_table.add_column("Condition", width=16)
    listings_table.add_column("Date", width=14)
    listings_table.add_column("Title")

    for item in listings:
        colour = _price_colour(item["sold_price"], median)
        price_text = Text(f"£{item['sold_price']:.2f}", style=f"bold {colour}")

        title = item["title"]
        url = item.get("url", "")
        title_text = Text(title)
        if url:
            title_text.stylize(f"link {url}")

        listings_table.add_row(price_text, item["condition"], item["date_sold"], title_text)

    console.print(listings_table)


def show_active_listings(listings: list[dict], median: float) -> None:
    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold dim",
                  title="[bold cyan]Current listings[/bold cyan]", title_justify="left")
    table.add_column("Price", no_wrap=True, width=10)
    table.add_column("Type", width=12)
    table.add_column("Condition", width=16)
    table.add_column("Title")

    for item in listings:
        colour = _price_colour(item["price"], median)
        price_text = Text(f"£{item['price']:.2f}", style=f"bold {colour}")

        title_text = Text(item["title"])
        if item.get("url"):
            title_text.stylize(f"link {item['url']}")

        table.add_row(price_text, item["listing_type"], item["condition"], title_text)

    console.print(table)


def show_verdict(price: float, median: float, label: str, colour: str) -> None:
    pct = (price / median) * 100

    lines = Text()
    lines.append("  Your price:   ", style="dim")
    lines.append(f"£{price:.2f}\n", style="bold")
    lines.append("  Median sold:  ", style="dim")
    lines.append(f"£{median:.2f}\n", style="bold")
    lines.append("  Position:     ", style="dim")
    lines.append(f"{pct:.0f}% of median\n\n", style="bold")
    lines.append("  Verdict:  ", style="dim")
    lines.append(label, style=f"bold {colour}")
    if colour == "green":
        lines.append("  ✓", style=colour)
    elif colour == "yellow":
        lines.append("  ~", style=colour)
    else:
        lines.append("  ✗", style=colour)

    console.print(Panel(lines, title="[bold]Deal Check[/bold]", border_style=colour))
