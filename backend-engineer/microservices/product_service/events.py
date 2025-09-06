import os
import redis, json
from dotenv import load_dotenv
load_dotenv()
r = redis.Redis.from_url(os.getenv("REDIS_URL","redis://redis:6379/0"), decode_responses=True)

def publish_inventory_change(product_id: int, delta: int):
    event = {"type": "inventory_changed", "product_id": product_id, "delta": delta}
    r.publish("inventory_events", json.dumps(event))
