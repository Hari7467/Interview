from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import crud, models, schemas
from database import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/products", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)


@app.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = crud.get_product(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@app.get("/products", response_model=list[schemas.ProductOut])
def list_all_products(db: Session = Depends(get_db)):
    return crud.get_all_products(db)



@app.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, updates: schemas.ProductUpdate, db: Session = Depends(get_db)):
    p = crud.get_product(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.update_product(db, p, updates.dict(exclude_unset=True))


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = crud.get_product(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete_product(db, p)
    return {"detail": "Product deleted successfully"}


@app.post("/products/{product_id}/adjust-stock", response_model=schemas.ProductOut)
def adjust_stock(product_id: int, payload: schemas.StockAdjustRequest, db: Session = Depends(get_db)):
    p = crud.get_product(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.adjust_stock(db, p, payload.delta)
