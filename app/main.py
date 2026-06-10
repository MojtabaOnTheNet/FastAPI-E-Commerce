from fastapi import FastAPI
from .routes import products, auth, cart, admin, user
from .core.config import settings

app = FastAPI(title="E Commerce")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(products.router)
app.include_router(cart.router)

""" @app.get("/", status_code=200)
async def root():

    return {"message": settings.INITIAL_SUPERUSER} """