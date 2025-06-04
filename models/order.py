from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
import enum

class OrderType(str, enum.Enum):
    buy = "buy"
    sell = "sell"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_symbol = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Float)
    order_type = Column(Enum(OrderType))

    user = relationship("User")
