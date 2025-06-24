# matching_engine/consumer.py
# ─────────────────────────── imports ────────────────────────────
import json, threading, asyncio, pika, uvicorn
from collections import defaultdict, deque
from datetime   import datetime, UTC          # tz-aware stamps
from typing     import Dict, Deque, Any

from fastapi import FastAPI, WebSocket
from matching_engine.ws_hub import register, unregister, broadcast
from services.trade_logger  import record_trade
from db.database            import SessionLocal          # DB for balance ops

# ────────────────────────── in-memory book ──────────────────────
OrderBookSide = Deque[Dict[str, Any]]
order_books: Dict[str, Dict[str, OrderBookSide]] = \
    defaultdict(lambda: {"buy": deque(), "sell": deque()})

def _add(symbol: str, side: str, order: dict):
    order_books[symbol][side].append(order)

def _remove_first(symbol: str, side: str):
    order_books[symbol][side].popleft()

def _find_order(order_id: int, user_id: int):
    """
    Return (symbol, side, order) or (None, None, None) if not found.
    """
    for sym, book in order_books.items():
        for side in ("buy", "sell"):
            for o in book[side]:
                if o["order_id"] == order_id and o["user_id"] == user_id:
                    return sym, side, o
    return None, None, None

# ───────────────────────── matching logic ───────────────────────
def process_new(order: dict):
    sym  = order["stock_symbol"].upper()
    side = order["order_type"]             # buy / sell
    opp  = "sell" if side == "buy" else "buy"
    qty  = order["quantity"]
    px   = order["price"]

    remaining = qty
    while order_books[sym][opp] and remaining:
        top = order_books[sym][opp][0]
        tradable = (side == "buy"  and px >= top["price"]) or \
                   (side == "sell" and px <= top["price"])
        if not tradable:
            break

        trade_qty   = min(remaining, top["quantity"])
        trade_price = top["price"]

        print(f"[TRADE] {sym} {trade_qty} @ {trade_price}")

        record_trade(                        # handles DB + cash
            buyer_id   = order["user_id"] if side == "buy" else top["user_id"],
            seller_id  = top["user_id"]    if side == "buy" else order["user_id"],
            stock_symbol = sym,
            price      = trade_price,
            quantity   = trade_qty,
        )

        if loop:
            asyncio.run_coroutine_threadsafe(
                broadcast({
                    "symbol":   sym,
                    "price":    trade_price,
                    "quantity": trade_qty,
                    "timestamp": datetime.now(UTC).isoformat()
                }),
                loop
            )

        remaining        -= trade_qty
        top["quantity"]  -= trade_qty
        if top["quantity"] == 0:
            _remove_first(sym, opp)

    if remaining:                             # still open
        order["quantity"] = remaining
        _add(sym, side, order)
        print(f"[BOOK] ++ {side.upper()} {order}")

def process_amend(payload: dict):
    order_id = payload["order_id"]
    user_id  = payload["user_id"]
    fields   = payload["fields"]              # {"price": 118, "quantity": 15}

    sym, side, order = _find_order(order_id, user_id)
    if not order:
        print(f"[AMEND] order #{order_id} NOT found – ignored")
        return

    order.update(fields)
    print(f"[AMEND] order #{order_id} updated → {order}")

def process_cancel(payload: dict):
    order_id = payload["order_id"]
    user_id  = payload["user_id"]

    sym, side, order = _find_order(order_id, user_id)
    if not order:
        print(f"[CANCEL] order #{order_id} NOT found – ignored")
        return

    order_books[sym][side].remove(order)
    print(f"[CANCEL] order #{order_id} removed")

# ─────────────────────── RabbitMQ consumer ──────────────────────
def consume():
    conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    ch   = conn.channel()
    ch.queue_declare("order_queue")
    ch.queue_declare("order_amend_queue")
    ch.queue_declare("order_cancel_queue")

    def cb(_ch, _m, _p, body):
        msg = json.loads(body)
        kind = msg.get("kind") or "new"       # fallback for old producers

        if   kind == "new":    process_new(msg)
        elif kind == "amend":  process_amend(msg)
        elif kind == "cancel": process_cancel(msg)
        else:
            print(f"[WARN] unknown kind: {kind!r}")

    ch.basic_consume("order_queue",        cb, auto_ack=True)
    ch.basic_consume("order_amend_queue",  cb, auto_ack=True)
    ch.basic_consume("order_cancel_queue", cb, auto_ack=True)

    print("[ENGINE] Waiting for orders / amends / cancels …")
    ch.start_consuming()

# ───────────────────────── FastAPI app ──────────────────────────
api  = FastAPI(title="Order-Book API")
loop: asyncio.AbstractEventLoop | None = None

@api.on_event("startup")
async def _set_loop():                 # capture main event-loop for WS push
    global loop
    loop = asyncio.get_running_loop()

@api.websocket("/ws/trades")
async def ws_trades(ws: WebSocket):
    await register(ws)
    try:
        while True:
            await ws.receive_text()
    except Exception:
        unregister(ws)

@api.get("/order-book")
def get_all():
    return {s: {"buy": list(b["buy"]), "sell": list(b["sell"])}
            for s, b in order_books.items()}

@api.get("/order-book/{symbol}")
def get_one(symbol: str):
    b = order_books.get(symbol.upper(), {"buy": [], "sell": []})
    return {"symbol": symbol.upper(), "buy": list(b["buy"]), "sell": list(b["sell"])}

# ────────────────────────── launcher ────────────────────────────
if __name__ == "__main__":
    threading.Thread(target=consume, daemon=True).start()
    uvicorn.run(api, host="0.0.0.0", port=8001)
