
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .models import Product, ProductCreate, ProductUpdate, Cart, Order, UserSignup, UserLogin, SessionToken
from .memory_store import store


app = FastAPI(title="E-commerce API", version="1.0.0")
@app.post("/signup")
async def signup(user: UserSignup):
    ok = store.signup(user.username, user.password, user.role)
    if not ok:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "Signup successful"}

@app.post("/login", response_model=SessionToken)
async def login(user: UserLogin):
    session = store.login(user.username, user.password)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return session

@app.get("/products/search", response_model=List[Product])
async def search_products(query: str):
    return store.search_products(query)

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
        description=product.description,
        quantity=product.quantity,
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
        description=product_update.description,
        quantity=product_update.quantity if hasattr(product_update, 'quantity') else None,
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

@app.put("/cart/{product_id}/increase")
async def increase_cart_quantity(product_id: int, token: Optional[str] = Header(None)):
    user = store.get_user_by_token(token) if token else None
    user_id = user.username if user else "default_user"
    if not store.increase_cart_quantity(user_id, product_id):
        raise HTTPException(status_code=404, detail="Product not found in cart")
    return {"message": "Cart quantity increased"}

@app.put("/cart/{product_id}/decrease")
async def decrease_cart_quantity(product_id: int, token: Optional[str] = Header(None)):
    user = store.get_user_by_token(token) if token else None
    user_id = user.username if user else "default_user"
    if not store.decrease_cart_quantity(user_id, product_id):
        raise HTTPException(status_code=404, detail="Product not found in cart")
    return {"message": "Cart quantity decreased"}

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
    import os
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

# --- Add sample dataset if DB is empty ---
try:
    products = store.get_all_products()
    if not products:
        store.add_product(name="Sample Phone", price=299.99, description="A great phone.", quantity=10)
        store.add_product(name="Sample Laptop", price=899.99, description="A powerful laptop.", quantity=5)
        store.add_product(name="Sample Headphones", price=99.99, description="Noise-cancelling headphones.", quantity=20)
except Exception:
    # ignore DB errors during import/time of module load
    pass
