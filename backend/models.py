from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str


class ProductCreate(BaseModel):
    name: str
    price: float
    description: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None


class CartItem(BaseModel):
    product_id: int
    quantity: int


class Cart(BaseModel):
    items: List[CartItem] = []


class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int



class Order(BaseModel):
    id: int
    items: List[OrderItem]
    total: float
    created_at: datetime
    paid: bool = False


# User and Auth Models
class User(BaseModel):
    username: str
    password: str
    role: str  # 'buyer' or 'seller'

class UserSignup(BaseModel):
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class SessionToken(BaseModel):
    token: str
    username: str
    role: str
