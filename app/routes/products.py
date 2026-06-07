from fastapi import APIRouter, HTTPException, Query
from typing import Annotated, Any
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

    if not len(products):
        raise HTTPException(status_code=404, detail="No products found.")
    
    return {"data": products, "count": count}


@router.post("/", status_code=201, response_model=ProductPublic)
async def create_product(session: SessionDep, user: CurrentUserDep, product_request_model: ProductCreate):

    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    product = Product.model_validate(product_request_model)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get("/{product_id}", status_code=200, response_model=ProductPublic)
async def read_one_product(session: SessionDep, product_id: uuid.UUID):

    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="No product found.")

    return product


@router.put("/{product_id}", status_code=200, response_model=ProductPublic)
async def update_one_product(session: SessionDep, user: CurrentUserDep, product_id: uuid.UUID, product_request_model: ProductUpdate):

    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    product_db = session.get(Product, product_id)

    if not product_db:
        raise HTTPException(status_code=404, detail="No product found.")

    # exclude_unset = True to do not include field that are not sent
    product_data = product_request_model.model_dump(exclude_unset=True)
    product_db.sqlmodel_update(product_data)

    session.add(product_db)
    session.commit()
    session.refresh(product_db)
    return product_db


@router.delete("/{product_id}", status_code=204)
async def delete_one_product(session: SessionDep, user: CurrentUserDep, product_id: uuid.UUID):

    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="No product found.")
    
    session.delete(product)
    session.commit()


