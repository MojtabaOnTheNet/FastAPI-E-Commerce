import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, DateTime, Numeric, Relationship
from decimal import Decimal
from pydantic import EmailStr
from enum import Enum

def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)

created_at_field = Field(default_factory=get_datetime_utc, sa_type=DateTime(timezone=True))

class OrderStatus(str, Enum):
    pending = "pending"
    fulfilled = "fulfilled"
    cancelled = "cancelled"



# Models used on the database tables 👇
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=100)
    full_name: str | None = Field(default=None, max_length=100)
    hashed_password: str
    created_at: datetime = created_at_field
    is_active: bool = True
    is_superuser: bool = False

class Product(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=5, max_length=100, index=True)
    description: str | None = Field(default=None, min_length=5, max_length=200)
    created_at: datetime = created_at_field
    price: Decimal = Field(default=Decimal("0.00"), sa_type=Numeric(10, 2))
    quantity: int = Field(ge=0, default=0)
    cart_items: list["CartItem"] = Relationship(back_populates="product")


class Cart(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True, unique=True)
    items: list["CartItem"] = Relationship(back_populates="cart", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class CartItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    cart_id: uuid.UUID = Field(foreign_key="cart.id", index=True)
    product_id: uuid.UUID = Field(foreign_key="product.id", index=True)
    product: Product = Relationship(back_populates="cart_items")
    quantity: int = Field(default=1, ge=1)
    cart: Cart | None = Relationship(back_populates="items")

class Order(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    total_amount: Decimal = Field(default=Decimal("0.00"), sa_type=Numeric(10, 2))
    status: OrderStatus = OrderStatus.pending
    created_at: datetime = created_at_field
    order_items: list["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key="order.id", index=True)
    product_id: uuid.UUID = Field(foreign_key="product.id", index=True)
    quantity: int = Field(default=1, ge=1)
    price_at_purchase: Decimal = Field(default=Decimal("0.00"), sa_type=Numeric(10, 2))
    order: Order | None = Relationship(back_populates="order_items")



