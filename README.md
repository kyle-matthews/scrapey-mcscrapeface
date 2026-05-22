# scrapey-mcscrapeface

A personal CLI tool for researching eBay UK sold prices before buying items to resell. Give it a search term and it scrapes completed listings, crunches the numbers, and tells you whether the price you're looking at is a good deal.

## Features

- Scrapes eBay UK completed/sold listings via headless browser
- Displays median, mean, high, low, std dev, and result count
- Optional deal verdict: compares your price against the median and rates it **GOOD DEAL**, **FAIR**, or **OVERPRICED**
- Adjustable scrape depth (default 3 pages, ~180 results)
- `--headed` flag to open a visible browser if you ever hit a block

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

## Usage

```bash
# Research sold prices for a search term
scrapey "casio f91w"

# Include a deal verdict for the price you're looking at
scrapey "casio f91w" --price 12.50

# Scrape more pages for a larger sample
scrapey "casio f91w" --price 12.50 --pages 5

# Open a visible browser (useful if you hit a WAF block or VPN issue)
scrapey "casio f91w" --headed
```

## Example Output

```
╭─────────────────── casio f91w — sold prices ───────────────────╮
│                                                                  │
│   Median    £14.99                                               │
│   Mean      £15.42                                               │
│   Low       £6.00                                                │
│   High      £32.00                                               │
│   Std Dev   £4.81                                                │
│   Results   173                                                  │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯

 Price    Condition         Date          Title
 ───────────────────────────────────────────────────────────────
 £14.99   Pre-owned         15 May 2025   Casio F91W-1YEF Men's...
 £12.00   For parts/not…    14 May 2025   Casio F-91W watch
 ...

╭──────────────── Deal Check ────────────────╮
│                                             │
│   Your price:   £12.50                      │
│   Median sold:  £14.99                      │
│   Position:     83% of median               │
│                                             │
│   Verdict:  GOOD DEAL ✓                     │
│                                             │
╰─────────────────────────────────────────────╯
```

## Verdict Thresholds

| Position vs median | Verdict    |
|--------------------|------------|
| Below 85%          | GOOD DEAL  |
| 85% – 110%         | FAIR       |
| Above 110%         | OVERPRICED |

Thresholds are constants at the top of `src/scrapey/analytics.py` if you want to tune them.

## Troubleshooting

**"Access Denied" or no results returned**
eBay uses Akamai's WAF which blocks datacenter and VPN IP ranges. Run the tool from your home broadband connection, or try `--headed` to use a visible browser window.

**0 listings parsed**
eBay occasionally changes its HTML structure. Check `src/scrapey/parser.py` and update the CSS selectors to match the current markup.
