from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.order import Order, OrderType
from models.user import User
from pydantic import BaseModel
from utils.auth import create_access_token
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from services.queue import publish_order

load_dotenv()
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token validation error")

class OrderForm(BaseModel):
    stock_symbol: str
    quantity: int
    price: float
    order_type: OrderType

@router.post("/place-order")
def place_order(form: OrderForm, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = Order(
        user_id=current_user.id,
        stock_symbol=form.stock_symbol,
        quantity=form.quantity,
        price=form.price,
        order_type=form.order_type
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    order_data = {
        "order_id": order.id,
        "user_id": current_user.id,
        "stock_symbol": order.stock_symbol,
        "quantity": order.quantity,
        "price": order.price,
        "order_type": order.order_type
    }
    publish_order(order_data)
    return {"msg": "Order placed", "order_id": order.id}
