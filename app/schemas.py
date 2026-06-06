from sqlmodel import Field, SQLModel, DateTime, Numeric
from pydantic import EmailStr
from datetime import datetime
from decimal import Decimal
import uuid


# Models used for api endpoints ⚡

# Product 📦

# Models receieved via API 👇
class ProductBase(SQLModel):
    title: str = Field(min_length=5, max_length=100)
    description: str | None = Field(default=None, min_length=5, max_length=200)
    price: Decimal = Field(default=Decimal("0.00"))
    quantity: int = Field(ge=0, default=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=5, max_length=100)
    description: str | None = Field(default=None, min_length=5, max_length=200)
    price: Decimal | None = Field(default=None)
    quantity: int | None = Field(default=None)

# Models returned via API 👇
class ProductPublic(SQLModel):
    id: uuid.UUID
    title: str
    description: str
    price: Decimal
    quantity: int
    created_at: datetime

class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int


# User 👤

# Models receieved via API 👇
class UserBase(SQLModel):
    email: EmailStr = Field(max_length=100)
    full_name: str | None = Field(default=None, max_length=100)

class UserRegister(UserBase):
    password: str

class UserLogin(SQLModel):
    email: EmailStr
    password: str

# Models returned via API 👇
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime

# Add (UsersPublic) later for admin functionality

# Cart Item 🛒📦

# Models receieved via API 👇
class CartItemBase(SQLModel):
    product_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(CartItemBase):
    pass

# Models returned via API 👇
class CartItemRead(SQLModel):
    id: uuid.UUID
    product_id: uuid.UUID
    title: str
    price: Decimal
    quantity: int

# Cart 🛒

# Models returned via API 👇
class CartBase(SQLModel):
    items: list[CartItemRead]
    total: Decimal


class CartRead(CartBase):
    pass

# Order Item 🚚📦

# Models returned via API 👇
class OrderItemBase(SQLModel):
    product_id: uuid.UUID
    quantity: int
    price_at_purchase: Decimal

class OrderItemRead(OrderItemBase):
    pass

# Order 🚚

# Models returned via API 👇
class OrderBase(SQLModel):
    id: uuid.UUID
    total_amount: Decimal
    created_at: datetime

class OrderRead(OrderBase):
    items: list[OrderItemRead]
