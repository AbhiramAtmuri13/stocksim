from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    stock_symbol = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
