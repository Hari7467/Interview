import redis
import os
import json
from fastapi.encoders import jsonable_encoder

REDIS_URL = os.getenv("REDIS_URL")
r = redis.Redis.from_url(REDIS_URL)

def cache_order(order: dict):
    encoded = jsonable_encoder(order)
    r.set(f"order:{order['id']}", json.dumps(encoded), ex=3600)

def get_cached_order(order_id: int):
    data = r.get(f"order:{order_id}")
    if data:
        return json.loads(data)
    return None

def delete_cached_order(order_id: int):
    r.delete(f"order:{order_id}")
