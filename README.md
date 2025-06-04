# 🏦 StockSim – Distributed Stock Market Simulator

StockSim is a real-time, distributed stock market simulator where users can register, log in, and place buy/sell orders.  
It uses FastAPI, PostgreSQL, RabbitMQ, and a background matching engine written in Python.

## ⚙️ Tech Stack

- FastAPI (Python backend)
- PostgreSQL (database)
- SQLAlchemy (ORM)
- RabbitMQ (messaging queue)
- Docker + Docker Compose
- Pika (RabbitMQ client)
- JWT (user authentication)

## 🚀 Features

- Register and login securely with JWT
- Place buy/sell stock orders
- Orders are sent to a RabbitMQ queue
- Background service picks up and logs orders (order matching coming soon)

## 📁 Folder Structure

stocksim/
├── api/ # Route files (login, register, place order)
├── db/ # Database connection code
├── models/ # User and Order database models
├── services/ # Code that talks to RabbitMQ
├── matching_engine/ # Consumer that listens for new orders
├── utils/ # Password hashing and JWT token helpers
├── main.py # FastAPI entry point
├── docker-compose.yml # Docker setup for DB and RabbitMQ
├── .env # Secret keys and DB config (not pushed)
└── README.md # This file

## 🛠️ How to Run the Project (Local Setup)

1. Clone the project
   ```bash
   git clone https://github.com/AbhiramAtmuri13/stocksim.git
   cd stocksim

2. Create .env file with this content:
    DB_USER=stocksim_user
    DB_PASSWORD=stocksim_pass
    DB_NAME=stocksim
    DB_HOST=localhost
    DB_PORT=5432
    SECRET_KEY=your_jwt_secret
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30

3. Start PostgreSQL and RabbitMQ
    docker-compose up -d

4. Create and activate a virtual environment
    python -m venv venv
    venv\Scripts\activate   # or source venv/bin/activate

5. Install the Python Packages
    pip install -r requirements.txt

6. Run the FastAPI backend
    uvicorn main:app --reload

7. Run the order matching engine in a separate terminal
    python matching_engine/consumer.py


---

### ✅ 6. **Postman APIs to Test**
```markdown
## 📬 API Endpoints (Use in Postman)

### 1. Register
**POST** `http://localhost:8000/auth/register`  
**Body**:
```json
{
  "username": "abhiram",
  "email": "abhiram@example.com",
  "password": "mypassword"
}

### 2. Login
**POST** `http://localhost:8000/auth/login`  
**Body**:
```json
{
  "email": "abhiram@example.com",
  "password": "mypassword"
}

### 3. Place Order
**POST** `http://localhost:8000/orders/place-order`
**Headers**:
`Authorization: Bearer <your_token_here>`
`Content-Type: application/json`
**Body**:
```json
{
  "stock_symbol": "AAPL",
  "quantity": 10,
  "price": 150.00,
  "order_type": "buy"
}

```markdown
---
## 👨‍💻 Author

**Abhiram Atmuri**  
GitHub: [AbhiramAtmuri13](https://github.com/AbhiramAtmuri13)
