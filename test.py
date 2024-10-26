from api.utils import fetch_historical_trades

start = "2024-01-01T00:00:00Z"
end = "2024-01-10T00:00:00Z"

trades = fetch_historical_trades("AAPL", start, end)
print(trades)  # Check output structure
