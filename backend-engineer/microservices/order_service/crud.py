from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas
from cache import cache_order, get_cached_order, delete_cached_order
import os
import requests

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

def validate_user(user_id: int):
    headers = {"x-user-id": str(user_id)}
    resp = requests.get(f"{USER_SERVICE_URL}/users/me", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(404, "User ID does not exist")

def validate_product(product_id: int, quantity: int):
    resp = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    if resp.status_code != 200:
        raise HTTPException(404, "Product ID does not exist")
    product = resp.json()
    if product["quantity"] < quantity:
        raise HTTPException(400, "Insufficient product quantity")
    return product

def adjust_stock(product_id: int, delta: int):
    resp = requests.post(
        f"{PRODUCT_SERVICE_URL}/products/{product_id}/adjust_stock",
        json={"delta": delta}
    )
    if resp.status_code != 200:
        raise HTTPException(400, "Failed to adjust stock")
    return True

def create_order(db: Session, order_in: schemas.OrderCreate):
    validate_user(order_in.user_id)
    product = validate_product(order_in.product_id, order_in.quantity)
   
    order = models.Order(
        user_id=order_in.user_id,
        product_id=order_in.product_id,
        quantity=order_in.quantity,
        price=product["price"] * order_in.quantity,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    cache_order(schemas.OrderOut.from_orm(order).dict())
    return order

def list_orders(db: Session):
    return db.query(models.Order).order_by(models.Order.id.desc()).all()

def get_order(db: Session, order_id: int):
    cached = get_cached_order(order_id)
    if cached:
        return cached
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    cache_order(schemas.OrderOut.from_orm(order).dict())
    return order

def pay_order(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status == "paid":
        raise HTTPException(400, "Order already paid")

    order.status = "paid"
    db.add(order)
    db.commit()
    db.refresh(order)
    cache_order(schemas.OrderOut.from_orm(order).dict())
    return order

def update_order(db: Session, order_id: int, updates: schemas.OrderUpdate):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")


    if updates.quantity is not None and updates.quantity != order.quantity:
        delta = updates.quantity - order.quantity
        product = validate_product(order.product_id, max(0, delta))
        adjust_stock(order.product_id, -delta)
        order.quantity = updates.quantity
        order.price = product["price"] * order.quantity


    if updates.status:
        if updates.status == "cancelled" and order.status != "cancelled":
            adjust_stock(order.product_id, order.quantity)
            order.status = "cancelled"
        elif updates.status == "paid":
            if order.status != "paid":
                order.status = "paid"
        else:
            raise HTTPException(400, "Invalid status")

    db.add(order)
    db.commit()
    db.refresh(order)
    cache_order(schemas.OrderOut.from_orm(order).dict())
    return order
