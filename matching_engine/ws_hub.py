from typing import List
from fastapi import WebSocket

_clients: List[WebSocket] = []

async def register(ws: WebSocket):
    await ws.accept()
    _clients.append(ws)

def unregister(ws: WebSocket):
    if ws in _clients:
        _clients.remove(ws)

async def broadcast(data: dict):
    to_drop = []
    for ws in _clients:
        try:
            await ws.send_json(data)
        except Exception:
            to_drop.append(ws)
    for ws in to_drop:
        unregister(ws)
