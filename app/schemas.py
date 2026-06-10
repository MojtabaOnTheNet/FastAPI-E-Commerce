from sqlmodel import Field, SQLModel, DateTime, Numeric
from pydantic import EmailStr, field_validator
from datetime import datetime
from decimal import Decimal
from .models import OrderStatus
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
    price: Decimal = Field(default=Decimal("0.00"))
    quantity: int
    created_at: datetime

class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int

class ProductCartPublic(SQLModel):
    title: str
    description: str
    price: Decimal = Field(default=Decimal("0.00"))


# User 👤

# Models receieved via API 👇
class UserBase(SQLModel):
    email: EmailStr = Field(max_length=100)
    full_name: str | None = Field(default=None, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

class UserRegister(UserBase):
    password: str
    confirm_password: str

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class UserChangePassword(SQLModel):
    password: str
    new_password: str
    confirm_new_password: str
    

# Models returned via API 👇
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime

# Models only for admin 👇
class UserPrivate(UserBase):
    id: uuid.UUID
    created_at: datetime
    is_superuser: bool
    is_active: bool

class UsersPrivate(SQLModel):
    users: list[UserPrivate]

class UserPrivateChange(SQLModel):
    is_superuser: bool = False
    is_active: bool = True


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
    product: ProductCartPublic
    quantity: int

# Cart 🛒

# Models returned via API 👇
class CartBase(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    items: list[CartItemRead]
    total_amount: Decimal = Field(default=Decimal("0.00"))


class CartRead(CartBase):
    pass

# Models only for admin 👇
class CartsPrivate(SQLModel):
    carts: list[CartRead]

# Order Item 🚚📦

# Models returned via API 👇
class OrderItemBase(SQLModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    price_at_purchase: Decimal = Field(default=Decimal("0.00"))

class OrderItemRead(OrderItemBase):
    pass

# Order 🚚

# Models returned via API 👇
class OrderBase(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    total_amount: Decimal = Field(default=Decimal("0.00"))
    created_at: datetime
    status: OrderStatus

class OrderRead(OrderBase):
    order_items: list[OrderItemRead]

class OrdersRead(SQLModel):
    orders: list[OrderRead]


# Token 🔑
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str | None = None


