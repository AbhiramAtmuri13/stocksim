# main.py
from fastapi import FastAPI
from db.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from api.auth import router as auth_router
from api.order import router as order_router
from models.user import User
from models.order import Order
from models.trade import Trade
from api.trades import router as trades_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS if frontend will be separate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")

app.include_router(order_router, prefix="/orders")

app.include_router(trades_router, prefix="/trades")

@app.get("/")
def root():
    return {"message": "StockSim backend is running!"}
