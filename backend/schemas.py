from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
import uuid

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    hashed_password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None

# Product schemas
class ProductBase(BaseModel):
    isbn13: Optional[str] = None
    title: str
    subtitle: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[date] = None
    price: float = Field(..., gt=0)
    currency: str = "EUR"
    cover_image_url: Optional[str] = None
    description: Optional[str] = None
    product_type: str = "book"
    page_count: Optional[int] = None
    language: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: uuid.UUID
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Cart schemas
class CartItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(1, ge=1)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

class CartItemResponse(BaseModel):
    id: uuid.UUID
    product: ProductResponse
    quantity: int
    unit_price: float
    total_price: float
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: uuid.UUID
    items: List[CartItemResponse] = []
    subtotal: float = 0
    total_items: int = 0
    
    class Config:
        from_attributes = True

# Order schemas
class Address(BaseModel):
    first_name: str
    last_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    postal_code: str
    country: str
    phone: Optional[str] = None

class OrderCreate(BaseModel):
    shipping_address: Address
    billing_address: Optional[Address] = None
    payment_method: str
    shipping_cost: float = 0

class OrderItemResponse(BaseModel):
    product_id: uuid.UUID
    product_title: str
    quantity: int
    unit_price: float
    total_price: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    status: str
    subtotal: float
    shipping_cost: float
    tax_amount: float
    total_amount: float
    currency: str
    shipping_address: dict
    billing_address: dict
    payment_method: str
    payment_status: str
    items: List[OrderItemResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Search schemas
class SearchResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: List[ProductResponse]
    query: Optional[str] = None