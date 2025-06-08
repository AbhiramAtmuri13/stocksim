# ─────────────────────────── imports ────────────────────────────
import json, threading, asyncio, pika, uvicorn
from collections import defaultdict, deque
from datetime import datetime, UTC         # timezone-aware

from fastapi import FastAPI, WebSocket
from matching_engine.ws_hub import register, unregister, broadcast
from services.trade_logger import record_trade
from models.user import User               # ensures 'users' table in metadata
from models.order import Order             # optional; good for completeness

# ────────────────────────── in-memory book ──────────────────────
order_books = defaultdict(lambda: {"buy": deque(), "sell": deque()})

def add_order(symbol: str, side: str, order: dict):
    order_books[symbol][side].append(order)

def remove_first(symbol: str, side: str):
    order_books[symbol][side].popleft()

# ───────────────────────── matching logic ───────────────────────
def process_order(order: dict):
    sym  = order["stock_symbol"].upper()
    side = order["order_type"]               # "buy" / "sell"
    opp  = "sell" if side == "buy" else "buy"
    qty  = order["quantity"]
    px   = order["price"]

    remaining = qty
    while order_books[sym][opp] and remaining:
        top = order_books[sym][opp][0]
        match = (side == "buy"  and px >= top["price"]) or \
                (side == "sell" and px <= top["price"])

        if not match:
            break

        trade_qty = min(remaining, top["quantity"])
        print(f"[TRADE] {side.upper()} {trade_qty} {sym} @ {top['price']}")
        record_trade(
            buyer_id   = order["user_id"] if side == "buy" else top["user_id"],
            seller_id  = top["user_id"]   if side == "buy" else order["user_id"],
            stock_symbol = sym,
            price      = top["price"],
            quantity   = trade_qty,
        )

        # push live update to WebSocket clients
        if loop:
            asyncio.run_coroutine_threadsafe(
                broadcast({
                    "symbol":   sym,
                    "price":    top["price"],
                    "quantity": trade_qty,
                    "timestamp": datetime.now(UTC).isoformat()
                }),
                loop
            )

        remaining        -= trade_qty
        top["quantity"]  -= trade_qty
        if top["quantity"] == 0:
            remove_first(sym, opp)

    if remaining:
        order["quantity"] = remaining
        add_order(sym, side, order)
        print(f"[ORDER BOOK] Added unmatched {side.upper()} order: {order}")

# ─────────────────────── RabbitMQ consumer ──────────────────────
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

# ───────────────────────── FastAPI app ──────────────────────────
api = FastAPI(title="Order-Book API")
loop: asyncio.AbstractEventLoop | None = None   # will capture running loop

@api.on_event("startup")
async def _capture_loop():
    global loop
    loop = asyncio.get_running_loop()

# WebSocket feed
@api.websocket("/ws/trades")
async def trades_ws(ws: WebSocket):
    await register(ws)
    try:
        while True:
            await ws.receive_text()          # ignore client messages
    except Exception:
        unregister(ws)

# REST endpoints
@api.get("/order-book")
def all_books():
    return {s: {"buy": list(b["buy"]), "sell": list(b["sell"])}
            for s, b in order_books.items()}

@api.get("/order-book/{symbol}")
def one_book(symbol: str):
    book = order_books.get(symbol.upper(), {"buy": [], "sell": []})
    return {"symbol": symbol.upper(),
            "buy":  list(book["buy"]),
            "sell": list(book["sell"])}

# ────────────────────────── main entry ──────────────────────────
if __name__ == "__main__":
    threading.Thread(target=consume_orders, daemon=True).start()
    uvicorn.run(api, host="0.0.0.0", port=8001)
