# 🏦 StockSim – Distributed Stock Market Simulator

StockSim is a real-time, **distributed stock-market simulator**.  
Users can register, log in, and place buy/sell orders; a background matching
engine pairs compatible orders and stores trades.

| Layer | Tech |
|-------|------|
| API   | FastAPI (Python 3) |
| DB    | PostgreSQL + SQLAlchemy |
| Queue | RabbitMQ + Pika |
| Auth  | JWT (HS-256) |
| Infra | Docker & Docker Compose |

---

## 🚀 Features

- ✅ JWT-secured **register / login**
- ✅ **Place** buy & sell orders (`/orders/place-order`)
- ✅ Orders published to **RabbitMQ** queue
- ✅ **Background matching engine** consumes queue, matches orders, logs trades
- ⏳ Live WebSocket / portfolio endpoints *(coming next)*

---

## 📁 Project Layout

```text
stocksim/
├─ api/                # FastAPI route files (auth, orders)
├─ db/                 # Database connection (SQLAlchemy)
├─ models/             # ORM models: User, Order, Trade
├─ services/           # queue.py, trade_logger.py, etc.
├─ matching_engine/    # consumer.py + order_book helpers
├─ utils/              # password hashing & JWT utilities
├─ main.py             # FastAPI entry-point (port 8000)
├─ docker-compose.yml  # spins up Postgres + RabbitMQ
├─ requirements.txt
└─ README.md 

## 🛠️ Local Setup
1. Clone
git clone https://github.com/user_name/repo_name.git
cd stocksim

2. Create .env
DB_USER=stocksim_user
DB_PASSWORD=stocksim_pass
DB_NAME=stocksim
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=your_jwt_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
Never commit .env – it’s in .gitignore.

3. Start Postgres & RabbitMQ via Docker
docker-compose up -d 

4. Create & activate virtual-env
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

5. Install Python packages
pip install -r requirements.txt

6. Run FastAPI backend
uvicorn main:app --reload  

7. Run the matching engine (separate terminal)
python -m matching_engine.consumer   # also serves order-book on port 8001

Now you can:

Register → Login in Swagger (/auth/*)
Place orders at /orders/place-order
Watch the matching-engine console emit [TRADE] lines
Query live order-book: http://localhost:8001/order-book/AAPL