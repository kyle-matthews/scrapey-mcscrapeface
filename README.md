# scrapey-mcscrapeface

A personal CLI tool for researching eBay UK prices before buying items to resell. Give it a search term and it scrapes completed sold listings for pricing stats, then pulls current live listings so you can spot deals in real time.

## Features

- Scrapes eBay UK completed/sold listings and computes median, mean, high, low, and std dev
- Shows current live listings (Buy It Now + auctions) alongside the sold stats
- Prices colour-coded green/yellow/red based on where they sit relative to the sold median
- Item titles are clickable hyperlinks to the listing
- Optional deal verdict: rates a price you're considering as **GOOD DEAL**, **FAIR**, or **OVERPRICED**
- Filter by keyword, condition, and price range — affects stats, not just display
- Sort results by price or condition, ascending or descending
- Limit table rows for a cleaner view without affecting the stats
- Compact mode: stats panel only, no listing tables
- Page-by-page progress so you can see what's happening during scraping
- Saves your eBay session cookie so you only need to solve the CAPTCHA once
- Runs with a visible browser by default; use `--headless` to suppress the window

## Requirements

- Python 3.11+
- Works best on a home broadband connection (eBay blocks datacenter IPs)

## Installation

```bash
git clone https://github.com/kyle-matthews/scrapey-mcscrapeface.git
cd scrapey-mcscrapeface
pip install -e .
playwright install chromium
```

## First run

eBay will show a CAPTCHA the first time. The tool handles it automatically — a browser window opens, you solve it, and your session is saved to `~/.scrapey/cookies.json` for all future runs.

```bash
scrapey "casio f91w"
```

## Usage

```bash
# Basic research — sold stats + current listings
scrapey "casio f91w"

# Include a deal verdict for a price you're looking at
scrapey "casio f91w" --price 12.50

# Scrape more pages of sold listings for a larger sample (default: 3)
scrapey "casio f91w" --pages 5

# Strip irrelevant results from stats entirely (repeatable)
scrapey "thinkpad x60" --exclude x61 --exclude tablet

# Only include a specific condition in the stats
scrapey "thinkpad x60" --condition "Pre-owned"

# Cut outliers from the numbers
scrapey "thinkpad x60" --min-price 20 --max-price 250

# Sort by price, cheapest first — applies to both sold and active tables
scrapey "thinkpad x60" --sort price

# Sort by price, most expensive first
scrapey "thinkpad x60" --sort price --desc

# Cap table rows (stats still use all results)
scrapey "thinkpad x60" --limit 10

# Stats panel only — no listing tables
scrapey "thinkpad x60" --compact

# Run without a browser window
scrapey "casio f91w" --headless

# Everything at once
scrapey "thinkpad x60" --exclude x61 --condition "Pre-owned" --min-price 20 --sort price --limit 15 --price 45
```

## Example output

```
Scraping 'thinkpad x60'
  ↳ Sold listings — page 1/3…
  ↳ Sold listings — page 2/3…
  ↳ Sold listings — page 3/3…
  ↳ Active listings…

╭──────────────────── thinkpad x60 — sold prices ───────────────────────╮
│                                                                        │
│   Median    £89.20                                                     │
│   Mean      £99.76                                                     │
│   Low       £3.00                                                      │
│   High      £390.56                                                    │
│   Std Dev   £58.91                                                     │
│   Results   81                                                         │
│                                                                        │
╰────────────────────────────────────────────────────────────────────────╯

  Price      Condition      Date           Title
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  £35.00     Parts only     19 May 2026    Lenovo ThinkPad X61 - For...
  £47.97     Pre-owned      16 May 2026    IBM Lenovo thinkpad X61...
  £102.40    Pre-owned      16 May 2026    Lenovo ThinkPad X61s...

Current listings

  Price      Type           Condition      Title
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  £42.06     Auction        Pre-owned      Lenovo ThinkPad X61s...
  £64.26     Buy It Now     Pre-owned      IBM Lenovo thinkpad X61...
  £179.95    Buy It Now     Pre-owned      IBM Lenovo X60s Laptop...

╭──────────────── Deal Check ─────────────────╮
│                                              │
│   Your price:   £45.00                       │
│   Median sold:  £89.20                       │
│   Position:     50% of median                │
│                                              │
│   Verdict:  GOOD DEAL ✓                      │
│                                              │
╰──────────────────────────────────────────────╯
```

## Colour coding

Prices in both tables are coloured relative to the sold median:

| Colour | Position vs median | Meaning                       |
|--------|--------------------|-------------------------------|
| Green  | Below 85%          | Cheap relative to market      |
| Yellow | 85% – 110%         | Fair market value             |
| Red    | Above 110%         | Expensive relative to median  |

## Verdict thresholds

The same 85% / 110% boundaries apply to the `--price` verdict. Adjust them in `src/scrapey/analytics.py` (`GOOD_DEAL_THRESHOLD`, `OVERPRICED_THRESHOLD`).

## All options

| Flag | Description |
|------|-------------|
| `--price FLOAT` | Price you're considering — shows a deal verdict |
| `--pages N` | Pages of sold listings to scrape (default: 3, ~60 results each) |
| `--exclude WORD` | Remove listings with this word in the title. Repeatable |
| `--condition TEXT` | Only include listings matching this condition (e.g. `Pre-owned`) |
| `--min-price FLOAT` | Exclude listings below this price |
| `--max-price FLOAT` | Exclude listings above this price |
| `--sort [price\|condition]` | Sort both tables by this field |
| `--desc` | Reverse sort order |
| `--limit N` | Cap rows shown per table (stats use all results) |
| `--compact` | Stats panel only — skip listing tables |
| `--headless` | Run without a visible browser window |

## Troubleshooting

**"Access Denied" or no results**
eBay's WAF blocks datacenter and VPN IP ranges. Run from your home broadband, or disable your VPN.

**CAPTCHA on every run**
Delete `~/.scrapey/cookies.json` and run again to get a fresh session.

**0 listings parsed**
eBay occasionally redesigns their search page. Update the CSS selectors in `src/scrapey/parser.py` to match the new markup.

**No results after filtering**
Your filters may be too strict. Try widening `--min-price` / `--max-price`, removing an `--exclude`, or dropping the `--condition` filter.
