from pydantic import BaseModel, Field, constr, conint, confloat
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    sku: constr(strip_whitespace=True, min_length=1, max_length=64)
    name: constr(strip_whitespace=True, min_length=1, max_length=200)
    description: Optional[str] = None
    price: confloat(ge=0) = 0.0
class ProductCreate(ProductBase):
    quantity: conint(ge=0) = 0

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    quantity: Optional[int]

class ProductOut(ProductBase):
    id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class StockAdjustRequest(BaseModel):
    delta: int = Field(..., description="Positive to add stock, negative to reduce stock")

class StockReserveRequest(BaseModel):
    quantity: int = Field(..., ge=1, description="Quantity to reserve")

class ListProductsResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[ProductOut]
