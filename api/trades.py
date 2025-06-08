# api/trades.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.trade import Trade
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# ---------- Pydantic response ----------
class TradeOut(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    stock_symbol: str
    price: float
    quantity: int
    timestamp: datetime

    class Config:
        orm_mode = True

# ---------- DB helper ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Routes ----------
@router.get("/", response_model=List[TradeOut])
def list_trades(limit: int = 50, symbol: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Trade).order_by(Trade.timestamp.desc())
    if symbol:
        q = q.filter(Trade.stock_symbol == symbol.upper())
    return q.limit(limit).all()
