from db.database import SessionLocal
from models.trade import Trade

def record_trade(buyer_id, seller_id, stock_symbol, price, quantity):
    print(f"[LOGGING] Recording trade: {buyer_id=} {seller_id=} {stock_symbol=} {price=} {quantity=}")
    db = SessionLocal()
    try:
        trade = Trade(
            buyer_id=buyer_id,
            seller_id=seller_id,
            stock_symbol=stock_symbol,
            price=price,
            quantity=quantity
        )
        db.add(trade)
        db.commit()
    finally:
        db.close()

