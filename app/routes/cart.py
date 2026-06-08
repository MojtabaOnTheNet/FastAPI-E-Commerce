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
    if not len(cart.items):
        raise HTTPException(status_code=404, detail="Cart is empty.")
    return cart

@router.post("/", status_code=201, response_model=CartItemRead)
async def add_cart_item(user: CurrentUserDep, session: SessionDep, request_cart_item: CartItemCreate):
    cart = session.exec(select(Cart).where(Cart.user_id == user.id)).first()

    # If no cart exists, create one
    if not cart:
        cart = Cart(user_id = user.id)
        session.add(cart)
        session.commit()
        session.refresh(cart)

    cart_item = session.exec(select(CartItem).where(CartItem.product_id == request_cart_item.product_id).where(CartItem.cart_id == cart.id)).first()

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
