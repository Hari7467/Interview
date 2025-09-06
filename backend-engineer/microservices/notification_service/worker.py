import os, redis, json
from dotenv import load_dotenv
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL","redis://redis:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe("user_events")
pubsub.subscribe("order_events")
pubsub.subscribe("inventory_events")

print("Notification worker listening on channels...")

for msg in pubsub.listen():
    if msg["type"] != "message":
        continue
    data = json.loads(msg["data"])
    print("Event received:", data)
   
    if data.get("type") == "user_created":
        print(f"Send welcome email to {data.get('email')}")
    elif data.get("type") == "order_created":
        print(f"New order {data.get('order_id')} placed")
    elif data.get("type") == "inventory_changed":
        print(f"Inventory changed for {data.get('product_id')}: delta {data.get('delta')}")
