import requests
from datetime import datetime, timedelta
from config import API_KEY, API_SECRET

def fetch_historical_trades(symbol: str, start: str, end: str):
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/trades"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }
    params = {
        "start": start,
        "end": end,
        "limit": 1000  # Adjust as needed
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raise exception if request fails
    return response.json()

# Example usage
# trades = fetch_historical_trades("AAPL", "2023-01-01T00:00:00Z", "2023-01-10T00:00:00Z")

def fetch_stock_price(symbol: str):
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise exception if request fails
    data = response.json()
    return data.get("quote", {}).get("ap")  # "ap" is the ask price (latest price)

# Calculate Moving Average
def calculate_moving_average(prices: list, window: int = 5) -> list:
    moving_averages = []
    for i in range(len(prices) - window + 1):
        window_prices = prices[i:i + window]
        moving_averages.append(sum(window_prices) / window)
    return moving_averages
