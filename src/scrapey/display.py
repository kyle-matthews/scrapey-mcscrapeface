from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()


def show_stats(term: str, stats: dict, listings: list[dict]) -> None:
    summary = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    summary.add_column("Metric", style="dim")
    summary.add_column("Value", style="bold")

    summary.add_row("Median", f"£{stats['median']:.2f}")
    summary.add_row("Mean", f"£{stats['mean']:.2f}")
    summary.add_row("Low", f"£{stats['low']:.2f}")
    summary.add_row("High", f"£{stats['high']:.2f}")
    summary.add_row("Std Dev", f"£{stats['std_dev']:.2f}")
    summary.add_row("Results", str(stats["count"]))

    console.print(Panel(summary, title=f"[bold cyan]{term}[/bold cyan] — sold prices", border_style="cyan"))

    listings_table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold dim")
    listings_table.add_column("Price", style="bold green", no_wrap=True, width=10)
    listings_table.add_column("Condition", width=16)
    listings_table.add_column("Date", width=14)
    listings_table.add_column("Title")

    for item in listings:
        listings_table.add_row(
            f"£{item['sold_price']:.2f}",
            item["condition"],
            item["date_sold"],
            item["title"],
        )

    console.print(listings_table)


def show_verdict(price: float, median: float, label: str, colour: str) -> None:
    pct = (price / median) * 100

    lines = Text()
    lines.append(f"  Your price:   ", style="dim")
    lines.append(f"£{price:.2f}\n", style="bold")
    lines.append(f"  Median sold:  ", style="dim")
    lines.append(f"£{median:.2f}\n", style="bold")
    lines.append(f"  Position:     ", style="dim")
    lines.append(f"{pct:.0f}% of median\n\n", style="bold")
    lines.append(f"  Verdict:  ", style="dim")
    lines.append(f"{label}", style=f"bold {colour}")
    if colour == "green":
        lines.append("  ✓", style=colour)
    elif colour == "yellow":
        lines.append("  ~", style=colour)
    else:
        lines.append("  ✗", style=colour)

    console.print(Panel(lines, title="[bold]Deal Check[/bold]", border_style=colour))
