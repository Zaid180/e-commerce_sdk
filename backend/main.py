from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .models import Product, ProductCreate, ProductUpdate, Cart, Order, UserSignup, UserLogin, SessionToken
from .memory_store import store

app = FastAPI(title="E-commerce API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/products", response_model=Product)
async def add_product(product: ProductCreate):
    return store.add_product(
        name=product.name,
        price=product.price,
        description=product.description
    )

@app.get("/products", response_model=List[Product])
async def list_products():
    return store.get_all_products()

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = store.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product_update: ProductUpdate):
    product = store.update_product(
        product_id,
        name=product_update.name,
        price=product_update.price,
        description=product_update.description
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    if not store.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@app.post("/cart")
async def add_to_cart(product_id: int, quantity: int = 1, token: Optional[str] = Header(None)):
    user = store.get_user_by_token(token) if token else None
    user_id = user.username if user else "default_user"
    if not store.add_to_cart(user_id, product_id, quantity):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product added to cart"}

@app.get("/cart", response_model=Cart)
async def view_cart(token: Optional[str] = Header(None)):
    user = store.get_user_by_token(token) if token else None
    user_id = user.username if user else "default_user"
    return store.get_cart(user_id)

@app.delete("/cart/{product_id}")
async def remove_from_cart(product_id: int, token: Optional[str] = Header(None)):
    user = store.get_user_by_token(token) if token else None
    user_id = user.username if user else "default_user"
    store.remove_from_cart(user_id, product_id)
    return {"message": "Product removed from cart"}

@app.post("/checkout", response_model=Order)
async def checkout(token: Optional[str] = Header(None)):
    user = store.get_user_by_token(token) if token else None
    user_id = user.username if user else "default_user"
    order = store.checkout(user_id)
    if not order:
        raise HTTPException(status_code=400, detail="Cart is empty")
    return order

@app.get("/")
async def root():
    return {"message": "E-commerce API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
