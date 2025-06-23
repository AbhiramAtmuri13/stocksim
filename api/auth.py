from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.user import User
from utils.auth import hash_password, verify_password, create_access_token
from pydantic import BaseModel
from models.balance import Balance

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterForm(BaseModel):
    username: str
    email: str
    password: str

class LoginForm(BaseModel):
    email: str
    password: str

@router.post("/register")
def register_user(form: RegisterForm, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == form.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        username=form.username,
        email=form.email,
        hashed_password=hash_password(form.password)
    )
    db.add(new_user)
    db.flush()

    new_balance = Balance(
        user_id = new_user.id,
        cash = 10000.0
    )
    db.add(new_balance)
    
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully"}

@router.post("/login")
def login_user(form: LoginForm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.email).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
