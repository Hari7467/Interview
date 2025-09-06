import redis
import json
from typing import Optional
from schemas import ProductOut
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

PRODUCT_CACHE_PREFIX = "product:"

def cache_product(product: ProductOut):
    key = PRODUCT_CACHE_PREFIX + str(product.id)
    redis_client.set(key, json.dumps(product.dict()), ex=3600)

def get_cached_product(product_id: int) -> Optional[ProductOut]:
    key = PRODUCT_CACHE_PREFIX + str(product_id)
    data = redis_client.get(key)
    if data:
        return ProductOut.parse_raw(data)
    return None

def delete_cached_product(product_id: int):
    key = PRODUCT_CACHE_PREFIX + str(product_id)
    redis_client.delete(key)

def reserve_stock(product_id: int, quantity: int) -> bool:
    key = f"stock:{product_id}"
    with redis_client.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                current = int(redis_client.get(key) or 0)
                if current < quantity:
                    pipe.unwatch()
                    return False
                pipe.multi()
                pipe.set(key, current - quantity)
                pipe.execute()
                return True
            except redis.WatchError:
                continue

def release_stock(product_id: int, quantity: int):
    key = f"stock:{product_id}"
    redis_client.incrby(key, quantity)

def set_initial_stock(product_id: int, quantity: int):
    key = f"stock:{product_id}"
    redis_client.set(key, quantity)
