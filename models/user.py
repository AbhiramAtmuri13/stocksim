from sqlalchemy import Column, Integer, String
from db.database import Base
from models.balance import Balance
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    balance = relationship("Balance", back_populates="user", uselist=False)

