from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", status_code=200)
async def read_all_products():
    return {"message": "Products work!"} 