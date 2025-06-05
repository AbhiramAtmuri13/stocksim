from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.trade import Trade

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_trades(symbol: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Trade).order_by(Trade.timestamp.desc())
    if symbol:
        query = query.filter(Trade.stock_symbol == symbol.upper())
    return query.limit(limit).all()
