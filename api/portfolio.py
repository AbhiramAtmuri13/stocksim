from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.user import User
from utils.auth import get_current_user          # you already had this helper
from services.portfolio import get_user_positions

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def my_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_positions(current_user.id, db)
