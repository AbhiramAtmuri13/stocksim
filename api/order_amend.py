# api/order_amend.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import json, pika
from utils.auth import get_current_user
from db.database import SessionLocal

router = APIRouter(
    prefix="/orders",
    tags=["Orders – amend / cancel"]
)

# ---- Pydantic payloads -------------------------------------------------
class AmendPayload(BaseModel):
    price:     float  | None = Field(None, gt=0)
    quantity:  int    | None = Field(None, gt=0)

class CancelPayload(BaseModel):
    confirm: bool = True

# ---- Rabbit helper -----------------------------------------------------
def publish(queue: str, message: dict):
    conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    ch   = conn.channel()
    ch.queue_declare(queue=queue)
    ch.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message).encode()
    )
    conn.close()

# ---- PATCH (amend) -----------------------------------------------------
@router.patch("/{order_id}", summary="Amend an open order")
def amend_order(
    order_id: int,
    body: AmendPayload,
    user = Depends(get_current_user)
):
    if body.price is None and body.quantity is None:
        raise HTTPException(400, "Nothing to amend")

    publish("order_amend_queue", {
        "kind":      "amend",
        "order_id":  order_id,
        "user_id":   user.id,
        "fields":    body.dict(exclude_none=True)
    })
    return {"msg": "amend sent"}

# ---- DELETE (cancel) ---------------------------------------------------
@router.delete("/{order_id}", summary="Cancel an open order")
def cancel_order(
    order_id: int,
    body: CancelPayload,
    user = Depends(get_current_user)
):
    if not body.confirm:
        raise HTTPException(400, "Cancel not confirmed")

    publish("order_cancel_queue", {
        "kind":     "cancel",
        "order_id": order_id,
        "user_id":  user.id
    })
    return {"msg": "cancel sent"}
