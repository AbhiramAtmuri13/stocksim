from collections import defaultdict, deque

# { "AAPL": {"buy": deque([...]), "sell": deque([...])}, ... }
order_books = defaultdict(lambda: {"buy": deque(), "sell": deque()})

def add_order(symbol: str, side: str, order: dict):
    order_books[symbol][side].append(order)

def pop_best(symbol: str, side: str):
    """Return first order in the deque or None."""
    if order_books[symbol][side]:
        return order_books[symbol][side][0]
    return None

def remove_first(symbol: str, side: str):
    if order_books[symbol][side]:
        order_books[symbol][side].popleft()

def snapshot(symbol: str | None = None):
    """Return a serialisable copy of order-books (or single symbol)."""
    if symbol:
        book = order_books.get(symbol.upper(), {"buy": [], "sell": []})
        return {
            "symbol": symbol.upper(),
            "buy": list(book["buy"]),
            "sell": list(book["sell"]),
        }
    # whole book
    return {
        sym: {"buy": list(b["buy"]), "sell": list(b["sell"])}
        for sym, b in order_books.items()
    }
