from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Annotated
import uuid
from sqlmodel import select, func
from ..dependency import SessionDep, CurrentUserDep
from ..schemas import *
from ..models import *

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/product", status_code=201, response_model=ProductPublic)
async def create_product(session: SessionDep, user: CurrentUserDep, product_request_model: ProductCreate):
    print(user)
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    product = Product.model_validate(product_request_model)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.put("/product/{product_id}", status_code=200, response_model=ProductPublic)
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


@router.delete("/product/{product_id}", status_code=204)
async def delete_one_product(session: SessionDep, user: CurrentUserDep, product_id: uuid.UUID):

    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions.")

    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="No product found.")
    
    session.delete(product)
    session.commit()