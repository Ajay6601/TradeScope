from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    portfolios = relationship("Portfolio", back_populates="owner")
    trades = relationship("Trade", back_populates="owner")


class Portfolio(Base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="portfolios")


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String, nullable=False)
    trade_type = Column(String, nullable=False)  # "buy" or "sell"
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="trades")
