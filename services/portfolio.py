# services/portfolio.py
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from models.trade import Trade

def get_user_positions(user_id: int, db: Session):
    """
    Build current positions + P/L for a user from the trades table.
    """
    # ----- CASE helpers -------------------------------------------------
    qty_case = case(
        (Trade.buyer_id  == user_id,  Trade.quantity),
        (Trade.seller_id == user_id, -Trade.quantity),
        else_=0
    )
    spent_case = case(
        (Trade.buyer_id == user_id, Trade.price * Trade.quantity),
        else_=0          # sells don't raise cost basis
    )

    # ----- aggregate net qty & gross spent -----------------------------
    rows = (
        db.query(
            Trade.stock_symbol.label("sym"),
            func.sum(qty_case).label("net_qty"),
            func.sum(spent_case).label("gross_spent")
        )
        .group_by(Trade.stock_symbol)
        .having(func.sum(qty_case) != 0)           # ignore flat positions
        .all()
    )

    # ----- enrich with last price & compute P/L ------------------------
    positions = {}
    for sym, net_qty, gross_spent in rows:
        last_trade = (
            db.query(Trade)
              .filter(Trade.stock_symbol == sym)
              .order_by(Trade.timestamp.desc())
              .first()                # ← always 0-or-1 row, no exception
        )
        last_px = last_trade.price if last_trade else 0

        market_val = net_qty * last_px
        avg_cost   = abs(gross_spent) / abs(net_qty)
        pnl        = market_val - gross_spent

        positions[sym] = {
            "shares":     net_qty,
            "avg_cost":   round(avg_cost, 2),
            "invested":   round(gross_spent, 2),
            "last_px":    last_px,
            "market_val": round(market_val, 2),
            "pnl":        round(pnl, 2),
        }

    return positions
