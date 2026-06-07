from fastapi import FastAPI
from .routes import products, auth

app = FastAPI(title="E Commerce")

app.include_router(products.router)
app.include_router(auth.router)

""" @app.get("/", status_code=200)
async def root():
    return {"message": "I'm good!"} """