import os
from polygon import RESTClient
from dotenv import load_dotenv
from tools.market.market import get_share_price

load_dotenv(override=True)


polygon_api_key = os.getenv("POLYGON_API_KEY")
polygon_plan = os.getenv("POLYGON_PLAN")


client = RESTClient(polygon_api_key)

print(client.get_market_status().market)


#TODO: When asking for portfolio, instead of returning the symbols, we should have the company name alongside
#TODO: Have the portfolio persisted somewhere else