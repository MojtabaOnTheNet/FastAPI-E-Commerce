from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Annotated
import uuid
from sqlmodel import select, func
from ..dependency import SessionDep, CurrentUserDep, get_current_active_superuser
from ..schemas import *
from ..models import *

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_active_superuser)])

@router.post("/product", status_code=201, response_model=ProductPublic)
async def create_product(session: SessionDep, product_request_model: ProductCreate):

    product = Product.model_validate(product_request_model)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.put("/product/{product_id}", status_code=204)
async def update_one_product(session: SessionDep, product_id: uuid.UUID, product_request_model: ProductUpdate):

    product_db = session.get(Product, product_id)

    if not product_db:
        raise HTTPException(status_code=404, detail="No product found.")

    # exclude_unset = True to do not include field that are not sent
    product_data = product_request_model.model_dump(exclude_unset=True)
    product_db.sqlmodel_update(product_data)

    session.add(product_db)
    session.commit()
    session.refresh(product_db)


@router.delete("/product/{product_id}", status_code=204)
async def delete_one_product(session: SessionDep, product_id: uuid.UUID):

    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="No product found.")
    
    session.delete(product)
    session.commit()


@router.get("/carts/{user_id}", status_code=200, response_model=CartRead)
async def read_any_cart(user_id: uuid.UUID, session: SessionDep):
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()

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

@router.delete("/carts/{user_id}", status_code=204)
async def delete_any_cart(user_id: uuid.UUID, session: SessionDep):
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()

    if not cart:
        raise HTTPException(status_code=404, detail="No cart found.")

    session.delete(cart)
    session.commit()

@router.get("/orders", status_code=200, response_model=OrdersReadPrivate)
async def read_all_orders(session: SessionDep):
    orders = session.exec(select(Order)).all()

    if not orders:
        raise HTTPException(status_code=404, detail="No order found.")
    
    return OrdersReadPrivate(orders=orders)

@router.put("/orders/{order_id}", status_code=204)
async def change_order_status(order_id: uuid.UUID, session: SessionDep, request_change_status: OrderChangeStatusPrivate):
    order = session.get(Order, order_id)

    order.status = request_change_status.status

    session.add(order)
    session.commit()
    session.refresh(order)

@router.get("/users/", status_code=200, response_model=UsersPrivate)
async def read_all_users(session: SessionDep):
    users = session.exec(select(User)).all()

    return {"users": users}

@router.put("/users/{user_id}", status_code=204)
async def change_user_privileges(session: SessionDep, user_id: uuid.UUID, request_change_model: UserPrivateChange):
    user = session.get(User, user_id)

    change_data = request_change_model.model_dump(exclude_unset=True)
    user.sqlmodel_update(change_data)

    session.add(user)
    session.commit()
    session.refresh(user)

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(session: SessionDep, user_id: uuid.UUID):
    user = session.get(User, user_id)

    session.delete(user)
    session.commit()