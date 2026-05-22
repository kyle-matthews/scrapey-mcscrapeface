import statistics

GOOD_DEAL_THRESHOLD = 0.85
OVERPRICED_THRESHOLD = 1.10


def compute_stats(prices: list[float]) -> dict:
    return {
        "count": len(prices),
        "median": statistics.median(prices),
        "mean": statistics.mean(prices),
        "low": min(prices),
        "high": max(prices),
        "std_dev": statistics.stdev(prices) if len(prices) > 1 else 0.0,
    }


def verdict(price: float, median: float) -> tuple[str, str]:
    ratio = price / median
    if ratio < GOOD_DEAL_THRESHOLD:
        return "GOOD DEAL", "green"
    if ratio <= OVERPRICED_THRESHOLD:
        return "FAIR", "yellow"
    return "OVERPRICED", "red"
