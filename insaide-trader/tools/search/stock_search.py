import os
from agents import function_tool
from dotenv import load_dotenv
import requests


load_dotenv(override=True)

polygon_api_key = os.getenv("POLYGON_API_KEY")

@function_tool
def get_ticker_from_name(company_name: str):
    """
    Searches Polygon.io for the ticker symbol of a company name.
    """
    # The Tickers v3 endpoint is the best for 'search' functionality
    url = "https://api.polygon.io/v3/reference/tickers"
    
    params = {
        "search": company_name,
        "active": "true",    # Only show companies currently trading
        "market": "stocks",  # Filter out crypto/forex if not needed
        "type": "CS",        # Common Stock only
        "limit": 3,          # Just get the top 3 most relevant
        "apiKey": polygon_api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            results = data["results"]
            top_match = results[0]
            return top_match.get("ticker")
        else:
            return f"No results found for '{company_name}'."
            
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Polygon: {e}"