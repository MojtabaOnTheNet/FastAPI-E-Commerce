from fastapi import FastAPI
from routes import products

app = FastAPI(title="E Commerce")

app.include_router(products.router)

@app.get("/", status_code=200)
async def root():
    return {"message": "I'm good!"}