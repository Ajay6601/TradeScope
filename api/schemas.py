from pydantic import BaseModel

# Model for trading requests
class TradeRequest(BaseModel):
    symbol: str
    quantity: int
