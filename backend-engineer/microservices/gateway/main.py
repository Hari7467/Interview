from fastapi import FastAPI, Request, Header
from pydantic import BaseModel
import httpx
import time
import jwt
import os

app = FastAPI(title="Advanced API Gateway", version="1.0.0")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8002")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order_service:8003")

SERVICES = {
    "users": [USER_SERVICE_URL],
    "products": [PRODUCT_SERVICE_URL],
    "orders": [ORDER_SERVICE_URL],
}

lb_index = {"users": 0, "products": 0, "orders": 0}


SECRET_KEY = "mysecret"


def get_service_url(service_name: str):
    urls = SERVICES[service_name]
    idx = lb_index[service_name]
    url = urls[idx % len(urls)]
    lb_index[service_name] = (idx + 1) % len(urls)
    return url

async def forward_request_json(service_name: str, path: str, data: dict = None, extra_headers: dict = None, method: str = "POST"):
    url = f"{get_service_url(service_name)}{path}"
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    start = time.time()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(method, url, headers=headers, json=data)
        except httpx.RequestError as e:
            return {"error": f"Service unavailable: {e}"}, 503

    duration = round((time.time() - start) * 1000, 2)
    print(f"[GATEWAY] {method} {url} -> {service_name} ({duration} ms)")

    try:
        content = resp.json()
    except Exception:
        content = resp.text

    return content, resp.status_code


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ProductCreateRequest(BaseModel):
    sku: str
    name: str
    description: str
    price: float
    quantity: int

class OrderCreateRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

@app.post("/users/register")
async def register_user(payload: RegisterRequest):
    return await forward_request_json("users", "/auth/register", payload.dict())

@app.post("/users/login")
async def login_user(payload: LoginRequest):
    return await forward_request_json("users", "/auth/login", payload.dict())

@app.get("/users/me")
async def get_me(x_user_id: str = Header(...)):
    headers = {"x-user-id": x_user_id}
    return await forward_request_json("users", "/users/me", extra_headers=headers, method="GET")

@app.get("/products")
async def list_products():
    return await forward_request_json("products", "/products", method="GET")

@app.post("/products")
async def create_product(payload: ProductCreateRequest):
    return await forward_request_json("products", "/products", payload.dict())

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    return await forward_request_json("products", f"/products/{product_id}", method="GET")

@app.put("/products/{product_id}")
async def update_product(product_id: int, payload: ProductCreateRequest):
    return await forward_request_json("products", f"/products/{product_id}", payload.dict(), method="PUT")

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    return await forward_request_json("products", f"/products/{product_id}", method="DELETE")

@app.post("/products/{product_id}/adjust-stock")
async def adjust_stock(product_id: int, payload: dict):
    return await forward_request_json("products", f"/products/{product_id}/adjust-stock", payload)

@app.get("/orders")
async def list_orders():
    return await forward_request_json("orders", "/orders", method="GET")

@app.post("/orders")
async def create_order(payload: OrderCreateRequest):
    return await forward_request_json("orders", "/orders", payload.dict())

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    return await forward_request_json("orders", f"/orders/{order_id}", method="GET")

@app.patch("/orders/{order_id}")
async def update_order(order_id: int, payload: dict):
    return await forward_request_json("orders", f"/orders/{order_id}", payload, method="PATCH")

@app.post("/orders/{order_id}/pay")
async def pay_order(order_id: int):
    return await forward_request_json("orders", f"/orders/{order_id}/pay", method="POST")


@app.get("/health")
async def health():
    return {"status": "ok", "services": list(SERVICES.keys())}

@app.get("/")
async def index():
    return {"message": "Welcome to API Gateway"}
