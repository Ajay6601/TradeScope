from fastapi import APIRouter, Depends, HTTPException
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import Trade, Portfolio, User
from db.db_connection import get_db
from config import API_KEY, API_SECRET
from api.auth import get_current_user
from api.schemas import TradeRequest  # Assuming TradeRequest is defined in api/schemas
from api.utils import fetch_stock_price
from api.utils import fetch_historical_trades, calculate_moving_average
from datetime import datetime, timedelta

router = APIRouter()

# Initialize Alpaca Trading Client
client = TradingClient(API_KEY, API_SECRET, paper=True)

# Buy Stock Endpoint
@router.post("/buy")
async def buy_stock(
    trade_request: TradeRequest, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    symbol = trade_request.symbol
    quantity = trade_request.quantity

    # Place a market buy order via Alpaca
    try:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        client.submit_order(order_data=market_order_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing trade: {str(e)}")

    # Update user's portfolio
    portfolio_stmt = select(Portfolio).where(Portfolio.user_id == current_user.id, Portfolio.stock_symbol == symbol)
    portfolio_result = await db.execute(portfolio_stmt)
    portfolio_item = portfolio_result.scalar_one_or_none()

    if portfolio_item:
        portfolio_item.quantity += quantity  # Update existing portfolio
    else:
        new_portfolio_item = Portfolio(stock_symbol=symbol, quantity=quantity, user_id=current_user.id)
        db.add(new_portfolio_item)

    await db.commit()
    return {"message": f"Bought {quantity} shares of {symbol}"}

# Sell Stock Endpoint
@router.post("/sell")
async def sell_stock(
    trade_request: TradeRequest, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    symbol = trade_request.symbol
    quantity = trade_request.quantity

    # Check if user has enough shares to sell
    portfolio_stmt = select(Portfolio).where(Portfolio.user_id == current_user.id, Portfolio.stock_symbol == symbol)
    portfolio_result = await db.execute(portfolio_stmt)
    portfolio_item = portfolio_result.scalar_one_or_none()

    if not portfolio_item or portfolio_item.quantity < quantity:
        raise HTTPException(status_code=400, detail="Not enough shares to sell")

    # Place a market sell order via Alpaca
    try:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        client.submit_order(order_data=market_order_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing trade: {str(e)}")

    # Update user's portfolio
    portfolio_item.quantity -= quantity
    if portfolio_item.quantity == 0:
        await db.delete(portfolio_item)
    await db.commit()

    return {"message": f"Sold {quantity} shares of {symbol}"}

# Endpoint to get user's portfolio
@router.get("/portfolio")
async def get_portfolio(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Fetch the user's portfolio
    portfolio_stmt = select(Portfolio).where(Portfolio.user_id == current_user.id)
    portfolio_result = await db.execute(portfolio_stmt)
    portfolio = portfolio_result.scalars().all()

    if not portfolio:
        return {"message": "Portfolio is empty"}

    return {
        "username": current_user.username,
        "portfolio": [{"stock_symbol": item.stock_symbol, "quantity": item.quantity} for item in portfolio]
    }

# Endpoint to get user's trade history
@router.get("/trade-history")
async def get_trade_history(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Fetch the user's trade history
    trade_stmt = select(Trade).where(Trade.user_id == current_user.id).order_by(Trade.timestamp.desc())
    trade_result = await db.execute(trade_stmt)
    trades = trade_result.scalars().all()

    if not trades:
        return {"message": "No trade history available"}

    return {
        "username": current_user.username,
        "trade_history": [
            {
                "stock_symbol": trade.stock_symbol,
                "trade_type": trade.trade_type,
                "quantity": trade.quantity,
                "price": trade.price,
                "timestamp": trade.timestamp
            } for trade in trades
        ]
    }

# 1. Endpoint to Calculate Portfolio Value
@router.get("/portfolio/value")
async def get_portfolio_value(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    portfolio_stmt = select(Portfolio).where(Portfolio.user_id == current_user.id)
    portfolio_result = await db.execute(portfolio_stmt)
    portfolio = portfolio_result.scalars().all()

    total_value = 0.0
    for item in portfolio:
        price = fetch_stock_price(item.stock_symbol)  # Fetch current price
        total_value += price * item.quantity

    return {"total_portfolio_value": total_value}

# 2. Endpoint to Track Profit/Loss
@router.get("/portfolio/profit-loss")
async def get_profit_loss(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    trade_stmt = select(Trade).where(Trade.user_id == current_user.id)
    trade_result = await db.execute(trade_stmt)
    trades = trade_result.scalars().all()

    profit_loss = {}
    for trade in trades:
        current_price = fetch_stock_price(trade.stock_symbol)
        if trade.trade_type == "buy":
            profit_loss[trade.stock_symbol] = profit_loss.get(trade.stock_symbol, 0) + (current_price - trade.price) * trade.quantity
        elif trade.trade_type == "sell":
            profit_loss[trade.stock_symbol] = profit_loss.get(trade.stock_symbol, 0) - (current_price - trade.price) * trade.quantity

    return {"profit_loss": profit_loss}

# 3. Endpoint for Portfolio Diversity
@router.get("/portfolio/diversity")
async def get_portfolio_diversity(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    portfolio_stmt = select(Portfolio).where(Portfolio.user_id == current_user.id)
    portfolio_result = await db.execute(portfolio_stmt)
    portfolio = portfolio_result.scalars().all()

    total_value = 0.0
    stock_values = {}
    for item in portfolio:
        price = fetch_stock_price(item.stock_symbol)
        value = price * item.quantity
        stock_values[item.stock_symbol] = value
        total_value += value

    diversity = {symbol: (value / total_value) * 100 for symbol, value in stock_values.items()}
    return {"portfolio_diversity": diversity}


@router.get("/portfolio/historical-analysis/{symbol}")
async def historical_analysis(symbol: str, days: int = 30, db: AsyncSession = Depends(get_db)):
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Fetch historical data
    historical_prices = fetch_historical_trades(symbol, start, end).get("bars", [])
    if not historical_prices:
        raise HTTPException(status_code=404, detail="No historical data available")

    # Calculate moving averages based on closing prices
    closing_prices = [data['c'] for data in historical_prices if 'c' in data]
    moving_average = calculate_moving_average(closing_prices)

    return {
        "symbol": symbol,
        "historical_prices": historical_prices,
        "moving_average": moving_average
    }