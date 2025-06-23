from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from utils.auth import get_current_user
from models.balance import Balance
from models.user import User

router = APIRouter(
    prefix="/balance",
    tags=["Balance"]
)

# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", summary="Get current user's cash balance")
def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    balance = db.query(Balance).filter(Balance.user_id == current_user.id).first()
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return {"cash": balance.cash}
