import json, threading, pika
from fastapi import FastAPI
import uvicorn

# ----------  ORDER-BOOK in memory ----------
from collections import defaultdict, deque

order_books = defaultdict(lambda: {"buy": deque(), "sell": deque()})

def add_order(symbol, side, order):
    order_books[symbol][side].append(order)

def remove_first(symbol, side):
    order_books[symbol][side].popleft()

# ----------  TRADE LOGGER ----------
from services.trade_logger import record_trade
from models.user import User      # needed so 'users' table exists
from models.order import Order    # optional

# ----------  MATCHING LOGIC ----------
def process_order(order):
    sym  = order["stock_symbol"].upper()
    side = order["order_type"]                 # buy / sell
    opp  = "sell" if side == "buy" else "buy"
    qty  = order["quantity"]
    px   = order["price"]

    remaining = qty
    while order_books[sym][opp] and remaining:
        top = order_books[sym][opp][0]
        if (side == "buy"  and px >= top["price"]) or \
           (side == "sell" and px <= top["price"]):

            trade_qty = min(remaining, top["quantity"])
            print(f"[TRADE] {side.upper()} {trade_qty} {sym} @ {top['price']}")
            record_trade(
                buyer_id  = order["user_id"] if side == "buy" else top["user_id"],
                seller_id = top["user_id"]   if side == "buy" else order["user_id"],
                stock_symbol = sym,
                price    = top["price"],
                quantity = trade_qty,
            )
            remaining       -= trade_qty
            top["quantity"] -= trade_qty
            if top["quantity"] == 0:
                remove_first(sym, opp)
        else:
            break

    if remaining:
        order["quantity"] = remaining
        add_order(sym, side, order)
        print(f"[ORDER BOOK] Added unmatched {side.upper()} order: {order}")

# ----------  RABBITMQ CONSUMER ----------
def consume_orders():
    conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    ch   = conn.channel()
    ch.queue_declare(queue="order_queue")

    def cb(_ch, _m, _p, body):
        order = json.loads(body)
        print("\n[MATCHING ENGINE] Received order:", order)
        process_order(order)

    ch.basic_consume(queue="order_queue", on_message_callback=cb, auto_ack=True)
    print("[MATCHING ENGINE] Waiting for orders...")
    ch.start_consuming()

# ----------  SMALL FASTAPI APP ----------
api = FastAPI(title="Order-Book API")

@api.get("/order-book")
def all_books():
    return {sym: {"buy": list(b["buy"]), "sell": list(b["sell"])}
            for sym, b in order_books.items()}

@api.get("/order-book/{symbol}")
def one_book(symbol: str):
    print("🔍  API asked for", symbol, "book is:", order_books[symbol.upper()])
    b = order_books.get(symbol.upper(), {"buy": [], "sell": []})
    return {"symbol": symbol.upper(), "buy": list(b["buy"]), "sell": list(b["sell"])}

# ----------  RUN EVERYTHING ----------
if __name__ == "__main__":
    # thread 1: matching engine
    threading.Thread(target=consume_orders, daemon=True).start()
    # thread 2: mini API on port 8001
    uvicorn.run(api, host="0.0.0.0", port=8001)
