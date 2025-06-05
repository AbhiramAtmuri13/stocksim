from fastapi import FastAPI
from matching_engine.order_book import snapshot

app = FastAPI(title="Order-Book API")

@app.get("/order-book")
def whole_book():
    """Full snapshot of all symbols."""
    return snapshot()

@app.get("/order-book/{symbol}")
def single_book(symbol: str):
    """Snapshot for one symbol (upper-case)."""
    return snapshot(symbol)
