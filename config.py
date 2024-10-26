import os

# Store your Alpaca API Key and Secret
API_KEY = os.getenv("ALPACA_API_KEY", "PKTNQ5KPUUPT4V3USYXE")
API_SECRET = os.getenv("ALPACA_API_SECRET", "E0a35WxZo27yuVqS7ouhDKL33YdTh14HxarQdz4h")
# BASE_URL = "https://data.alpaca.markets/v2"  # Use paper trading API for testing
BASE_URL="https://paper-api.alpaca.markets"

DATABASE_URL="postgresql+asyncpg://trader:trader_password@localhost/trading_platform"

SECRET_KEY = "c3222fed746c44db8003cd986afc5711"  # Replace with the generated secret key
ALGORITHM = "HS256"  # Consistent algorithm for JWT
