from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import crud, schemas, models
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service")

@app.post("/orders", response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, order)

@app.get("/orders", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)

@app.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return crud.get_order(db, order_id)

@app.post("/orders/{order_id}/pay", response_model=schemas.OrderOut)
def pay_order(order_id: int, db: Session = Depends(get_db)):
    return crud.pay_order(db, order_id)

@app.patch("/orders/{order_id}", response_model=schemas.OrderOut)
def update_order(order_id: int, updates: schemas.OrderUpdate, db: Session = Depends(get_db)):
    return crud.update_order(db, order_id, updates)
