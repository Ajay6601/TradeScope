from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from config import API_KEY, API_SECRET
from datetime import datetime

# Initialize Alpaca Historical Data Client
client = StockHistoricalDataClient(API_KEY, API_SECRET)

async def get_stock_price(symbol: str):
    """
    Fetch the latest stock price using Alpaca's stock bars.
    """
    try:
        # Create a request to fetch the latest bar
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Minute,  # You can use TimeFrame.Day for daily prices
            start=datetime.now().isoformat(),  # Fetching the most recent bar
            limit=1  # Limit to the most recent bar
        )
        
        # Get the bar data
        bars = client.get_stock_bars(request_params)
        
        # Extract the latest bar and return the close price
        latest_bar = bars[symbol][0]  # Access the first (most recent) bar
        print(f"Latest bar data: {latest_bar}")
        
        # Return the close price from the most recent bar
        return latest_bar.close
    except Exception as e:
        print(f"Error fetching stock price: {e}")
        return None
