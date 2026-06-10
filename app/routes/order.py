from fastapi import APIRouter, HTTPException, Query
from typing import Annotated
import uuid
from sqlmodel import select, func
from ..dependency import SessionDep, CurrentUserDep
from ..schemas import *
from ..models import *

router = APIRouter(prefix="/order", tags=["Order"])


@router.post("/checkout", status_code=201)
async def checkout_cart(user: CurrentUserDep, session: SessionDep):
    cart = session.exec(select(Cart).where(Cart.user_id == user.id)).first()

    if not cart:
        raise HTTPException(status_code=404, detail="No cart found.")

    cart_items = session.exec(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)).all()
    
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty.")
    
    # Calculate the total price of the cart
    total = session.exec(
        select(func.sum(CartItem.quantity * Product.price))
        .join(Product, CartItem.product_id == Product.id)
        .where(CartItem.cart_id == cart.id)
    ).one()

    

    # create a new order
    order = Order(user_id = user.id, total_amount=total)
    session.add(order)
    session.commit()
    session.refresh(order)

    # add items to the order
    for item in cart_items:
        order_item = OrderItem(
            order_id = order.id,
            product_id = item.product_id,
            quantity = item.quantity,
            price_at_purchase = item.product.price
        )
        session.add(order_item)
        session.commit()
        session.refresh(order_item)
    
    # after everything is done, delete the cart
    session.delete(cart)
    session.commit()


    return {"message": "Order successfully submitted."}


@router.get("/", status_code=200, response_model=OrdersRead)
async def read_all_orders(user: CurrentUserDep, session: SessionDep):
    orders = session.exec(select(Order).where(Order.user_id == user.id)).all()

    if not orders:
        raise HTTPException(status_code=404, detail="No order found.")
    
    return OrdersRead(orders=orders)
    
    