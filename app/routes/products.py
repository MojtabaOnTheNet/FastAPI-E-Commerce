from fastapi import APIRouter, HTTPException, Query
from typing import Annotated
import uuid
from sqlmodel import select, func
from ..dependency import SessionDep, CurrentUserDep
from ..schemas import *
from ..models import *


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", status_code=200, response_model=ProductsPublic)
async def read_all_products(session: SessionDep, limit: Annotated[int, Query(le=100)] = 100, offset: int = 0):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    count = session.exec(select(func.count(Product.id))).one()
    
    return {"data": products, "count": count}


@router.get("/{product_id}", status_code=200, response_model=ProductPublic)
async def read_one_product(session: SessionDep, product_id: uuid.UUID):

    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="No product found.")

    return product





