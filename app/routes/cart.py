from fastapi import APIRouter, HTTPException, Query
from typing import Annotated
import uuid
from sqlmodel import select, func
from ..dependency import SessionDep, CurrentUserDep
from ..schemas import *
from ..models import *

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", status_code=200, response_model=CartRead)
async def read_all_cart_items(user: CurrentUserDep, session: SessionDep):
    cart = session.exec(select(Cart).where(Cart.user_id == user.id)).first()

    if not cart:
        raise HTTPException(status_code=404, detail="No cart found.")

    # Calculate the total price of the cart
    total = session.exec(
        select(func.sum(CartItem.quantity * Product.price))
        .join(Product, CartItem.product_id == Product.id)
        .where(CartItem.cart_id == cart.id)
    ).one()
    
    if not len(cart.items):
        raise HTTPException(status_code=404, detail="Cart is empty.")
    
    return CartRead(
        **cart.model_dump(),
        items=cart.items,
        total_amount=total
        )

@router.post("/", status_code=201, response_model=CartItemRead)
async def add_cart_item(user: CurrentUserDep, session: SessionDep, request_cart_item: CartItemCreate):
    cart = session.exec(select(Cart).where(Cart.user_id == user.id)).first()

    # Handle product validation
    product = session.exec(select(Product).where(Product.id == request_cart_item.product_id)).first()
    if not product:
        raise HTTPException(status_code=404, detail="No product found.")

    # If no cart exists, create one
    if not cart:
        cart = Cart(user_id = user.id)
        session.add(cart)
        session.commit()
        session.refresh(cart)

    cart_item = session.exec(
        select(CartItem)
        .where(CartItem.product_id == request_cart_item.product_id)
        .where(CartItem.cart_id == cart.id)).first()

    # If no cart item with the current product exists, create one
    if not cart_item:
        cart_item = CartItem.model_validate({
            **request_cart_item.model_dump(),
            "cart_id": cart.id
        })
        session.add(cart_item)
        session.commit()
        session.refresh(cart_item)
        
    # Else if the cart item exists, update the quantity
    else:
        cart_item.quantity += request_cart_item.quantity

        session.add(cart_item)
        session.commit()
        session.refresh(cart_item)

    return cart_item

@router.get("/{cart_item_id}", status_code=200, response_model=CartItemRead)
async def read_cart_item(user: CurrentUserDep, session: SessionDep, cart_item_id: uuid.UUID):
    cart_item = session.exec(
        select(CartItem)
        .join(Cart)
        .where(Cart.user_id == user.id)
        .where(CartItem.id == cart_item_id)).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="No cart item found.")
    
    return cart_item

@router.put("/{cart_item_id}", status_code=201, response_model=CartItemUpdate)
async def update_cart_item(user: CurrentUserDep, session: SessionDep, cart_item_id: uuid.UUID, request_quantity: Annotated[int, Query(ge=1, lt=1000)]):
    cart_item = session.exec(
        select(CartItem)
        .join(Cart)
        .where(Cart.user_id == user.id)
        .where(CartItem.id == cart_item_id)).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="No cart item found.")
    
    cart_item.quantity = request_quantity

    session.add(cart_item)
    session.commit()
    session.refresh(cart_item)


    return cart_item

@router.delete("/{cart_item_id}", status_code=204)
async def delete_cart_item(user: CurrentUserDep, session: SessionDep, cart_item_id: uuid.UUID):
    cart_item = session.exec(
        select(CartItem)
        .join(Cart)
        .where(Cart.user_id == user.id)
        .where(CartItem.id == cart_item_id)).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="No cart item found.")
    
    session.delete(cart_item)
    session.commit()

    # Delete entire card if no items remain
    cart = session.exec(select(Cart).where(Cart.user_id == user.id)).first()

    if not len(cart.items):
        session.delete(cart)
        session.commit()

