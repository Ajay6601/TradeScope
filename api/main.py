from fastapi import FastAPI
from api.user import router as user_router
from api.market_data import get_stock_price
from api.trades import router as trade_router
from api.websocket import router as websocket_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Trading Platform"}

app.include_router(user_router, prefix="/users")
app.include_router(trade_router, prefix="/trades")
app.include_router(websocket_router, prefix="/ws")


@app.get("/price/{symbol}")
async def get_price(symbol: str):
    price = await get_stock_price(symbol)
    return {"symbol": symbol, "price": price}



