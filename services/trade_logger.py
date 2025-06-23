from db.database import SessionLocal
from models.trade import Trade
from models.balance import Balance

def record_trade(buyer_id, seller_id, stock_symbol, price, quantity):
    db = SessionLocal()
    try:
        # Insert the trade record
        trade = Trade(
            buyer_id=buyer_id,
            seller_id=seller_id,
            stock_symbol=stock_symbol,
            price=price,
            quantity=quantity
        )
        db.add(trade)

        total_cost = price * quantity

        # Update buyer and seller balances
        buyer_balance = db.query(Balance).filter(Balance.user_id == buyer_id).first()
        if buyer_balance:
            buyer_balance.cash -= total_cost

        seller_balance = db.query(Balance).filter(Balance.user_id == seller_id).first()
        if seller_balance:
            seller_balance.cash += total_cost

        db.commit()

        print(f"[LOGGING] Trade recorded and balances updated: buyer -{total_cost}, seller +{total_cost}")
        print(f"[BALANCE] Buyer New Cash: {buyer_balance.cash}, Seller New Cash: {seller_balance.cash}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to record trade: {e}")
    finally:
        db.close()
