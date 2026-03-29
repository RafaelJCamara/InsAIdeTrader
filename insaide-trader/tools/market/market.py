from agents import function_tool
from polygon import RESTClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import random
from .database import write_market, read_market

load_dotenv(override=True)

polygon_api_key = os.getenv("POLYGON_API_KEY")

def is_market_open() -> bool:
    client = RESTClient(polygon_api_key)
    market_status = client.get_market_status()
    return market_status.market == "open"


def get_all_share_prices_polygon_eod() -> dict[str, float]:
    client = RESTClient(polygon_api_key)

    probe = client.get_previous_close_agg("SPY")[0]
    last_close = datetime.fromtimestamp(probe.timestamp / 1000, tz=timezone.utc).date()

    results = client.get_grouped_daily_aggs(last_close, adjusted=True, include_otc=False)
    return {result.ticker: result.close for result in results}


@function_tool
def get_market_for_prior_date(today):
    """Gets the market data information for the prior date from the data passed.

    Args:
        today (DateTime): The reference date to get the market data for. The function will get the market data for the prior date.

    Returns:
        dict[str, float]: A dictionary mapping stock symbols to their prices.
    """
    
    print(f"Getting market data for prior date based on reference date {today}...")
    market_data = read_market(today)
    if not market_data:
        print("No market data found for prior date, fetching from API...")
        market_data = get_all_share_prices_polygon_eod()
        write_market(today, market_data)
        
    print(f"Market data for prior date: {market_data}")
    return market_data

def get_share_price_polygon_eod(symbol) -> float:
    today = datetime.now().date().strftime("%Y-%m-%d")
    market_data = get_market_for_prior_date(today)
    print(f"Market data for {today}: {market_data}")
    return market_data.get(symbol, 0.0)


def get_share_price_polygon_min(symbol) -> float:
    client = RESTClient(polygon_api_key)
    result = client.get_snapshot_ticker("stocks", symbol)
    return result.min.close or result.prev_day.close

def get_share_price(symbol) -> float:
    if polygon_api_key:
        try:
            return get_share_price_polygon_eod(symbol)
        except Exception as e:
            print(f"Was not able to use the polygon API due to {e}; using a random number")
    return float(random.randint(1, 100))