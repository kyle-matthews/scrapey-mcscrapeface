# scrapey-mcscrapeface

A personal CLI tool for researching eBay UK prices before buying items to resell. Give it a search term and it scrapes completed sold listings for pricing stats, then pulls current live listings so you can spot deals in real time.

## Features

- Scrapes eBay UK completed/sold listings and computes median, mean, high, low, and std dev
- Shows current live listings (Buy It Now + auctions) alongside the sold stats
- Prices colour-coded green/yellow/red based on where they sit relative to the sold median
- Item titles are clickable hyperlinks to the listing
- Optional deal verdict: rates a price you're considering as **GOOD DEAL**, **FAIR**, or **OVERPRICED**
- Sort results by price or condition, ascending or descending
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

# Sort by price, cheapest first (applies to both sold and active tables)
scrapey "casio f91w" --sort price

# Sort by price, most expensive first
scrapey "casio f91w" --sort price --desc

# Group by condition
scrapey "casio f91w" --sort condition

# Run without a browser window
scrapey "casio f91w" --headless
```

## Example Output

```
╭──────────────────── casio f91w — sold prices ─────────────────────╮
│                                                                     │
│   Median    £14.99                                                  │
│   Mean      £15.42                                                  │
│   Low       £6.00                                                   │
│   High      £32.00                                                  │
│   Std Dev   £4.81                                                   │
│   Results   173                                                     │
│                                                                     │
╰─────────────────────────────────────────────────────────────────────╯

  Price      Condition      Date           Title
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  £14.99     Pre-owned      15 May 2026    Casio F91W-1YEF Men's...
  £12.00     Parts only     14 May 2026    Casio F-91W watch
  £18.50     Pre-owned      12 May 2026    Casio F-91W Classic...

Current listings

  Price      Type           Condition      Title
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  £11.00     Buy It Now     Pre-owned      Casio F-91W Digital Watch
  £14.95     Buy It Now     Brand New      Casio F91W-1YEF
  £22.00     Auction        Pre-owned      Casio Classic F91W...

╭──────────────── Deal Check ─────────────────╮
│                                              │
│   Your price:   £12.50                       │
│   Median sold:  £14.99                       │
│   Position:     83% of median                │
│                                              │
│   Verdict:  GOOD DEAL ✓                      │
│                                              │
╰──────────────────────────────────────────────╯
```

## Colour coding

Prices in both tables are coloured relative to the sold median:

| Colour | Position vs median | Meaning                        |
|--------|--------------------|--------------------------------|
| Green  | Below 85%          | Cheap — sold below market      |
| Yellow | 85% – 110%         | Fair market value              |
| Red    | Above 110%         | Expensive relative to median   |

## Verdict thresholds

The same 85% / 110% boundaries apply to the `--price` verdict. Adjust them in `src/scrapey/analytics.py` (`GOOD_DEAL_THRESHOLD`, `OVERPRICED_THRESHOLD`).

## Troubleshooting

**"Access Denied" or no results**
eBay's WAF blocks datacenter and VPN IP ranges. Run from your home broadband, or disable your VPN.

**CAPTCHA on every run**
Delete `~/.scrapey/cookies.json` and run again to get a fresh session.

**0 listings parsed**
eBay occasionally redesigns their search page. Update the CSS selectors in `src/scrapey/parser.py` to match the new markup.
