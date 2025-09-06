from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
import models, schemas
from cache import set_initial_stock, cache_product, delete_cached_product

def create_product(db: Session, product_in: schemas.ProductCreate) -> models.Product:

    if get_product_by_sku(db, product_in.sku):
        raise HTTPException(status_code=400, detail="SKU already exists")

    p = models.Product(
        sku=product_in.sku,
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        quantity=product_in.quantity,
    )
    db.add(p)
    db.commit()
    db.refresh(p)


    try:
        set_initial_stock(p.id, p.quantity)
        cache_product(schemas.ProductOut.from_orm(p))
    except Exception as e:
        print("Redis cache error:", e)

    return p

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_sku(db: Session, sku: str):
    return db.query(models.Product).filter(models.Product.sku == sku).first()

def get_all_products(db: Session):
    return db.query(models.Product).order_by(models.Product.id.desc()).all()


def update_product(db: Session, product: models.Product, updates: dict):
    for k, v in updates.items():
        if v is not None and hasattr(product, k):
            setattr(product, k, v)
    db.add(product)
    db.commit()
    db.refresh(product)

   
    try:
        cache_product(schemas.ProductOut.from_orm(product))
    except Exception as e:
        print("Redis cache error:", e)

    return product

def delete_product(db: Session, product: models.Product):
    try:
        delete_cached_product(product.id)
    except Exception as e:
        print("Redis cache delete error:", e)

    db.delete(product)
    db.commit()

def adjust_stock(db: Session, product: models.Product, delta: int):
    new_qty = product.quantity + delta
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    product.quantity = new_qty
    db.add(product)
    db.commit()
    db.refresh(product)

    
    try:
        set_initial_stock(product.id, product.quantity)
        cache_product(schemas.ProductOut.from_orm(product))
    except Exception as e:
        print("Redis cache error:", e)

    return product
