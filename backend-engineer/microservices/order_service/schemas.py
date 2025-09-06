from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class OrderUpdate(BaseModel):
    quantity: Optional[int]
    status: Optional[str]  

class OrderOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    price: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  
