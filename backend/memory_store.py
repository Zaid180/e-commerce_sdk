from typing import Dict, List, Optional
from datetime import datetime
import secrets
from .models import Product, Cart, Order, OrderItem, User, SessionToken, CartItem
from .db_store import get_db


class MemoryStore:
    def __init__(self):
        with get_db() as db:
            if 'products' not in db:
                db['products'] = {}
            if 'carts' not in db:
                db['carts'] = {}
            if 'orders' not in db:
                db['orders'] = {}
            if 'users' not in db:
                db['users'] = {}
            if 'sessions' not in db:
                db['sessions'] = {}
            if 'next_product_id' not in db:
                db['next_product_id'] = 1
            if 'next_order_id' not in db:
                db['next_order_id'] = 1
    def search_products(self, query: str):
        query = query.lower()
        with get_db() as db:
            return [p for p in db['products'].values() if query in p.name.lower() or query in p.description.lower()]
    def signup(self, username: str, password: str, role: str) -> bool:
        with get_db() as db:
            if username in db['users']:
                return False
            db['users'][username] = User(username=username, password=password, role=role)
            db.sync()
            return True

    def login(self, username: str, password: str) -> Optional[SessionToken]:
        with get_db() as db:
            user = db['users'].get(username)
            if not user or user.password != password:
                return None
            token = secrets.token_hex(16)
            session = SessionToken(token=token, username=username, role=user.role)
            db['sessions'][token] = session
            db.sync()
            return session

    def get_user_by_token(self, token: str) -> Optional[User]:
        with get_db() as db:
            session = db['sessions'].get(token)
            if not session:
                return None
            return db['users'].get(session.username)

    def add_product(self, name: str, price: float, description: str) -> Product:
        with get_db() as db:
            pid = db['next_product_id']
            product = Product(
                id=pid,
                name=name,
                price=price,
                description=description
            )
            db['products'][pid] = product
            db['next_product_id'] += 1
            db.sync()
            return product

    def get_product(self, product_id: int) -> Optional[Product]:
        with get_db() as db:
            return db['products'].get(product_id)

    def get_all_products(self) -> List[Product]:
        with get_db() as db:
            return list(db['products'].values())

    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        with get_db() as db:
            if product_id not in db['products']:
                return None
            product = db['products'][product_id]
            for key, value in kwargs.items():
                if value is not None:
                    setattr(product, key, value)
            db['products'][product_id] = product
            db.sync()
            return product

    def delete_product(self, product_id: int) -> bool:
        with get_db() as db:
            if product_id in db['products']:
                del db['products'][product_id]
                db.sync()
                return True
            return False

    def get_cart(self, user_id: str) -> Cart:
        with get_db() as db:
            if user_id not in db['carts']:
                db['carts'][user_id] = Cart()
            return db['carts'][user_id]

    def add_to_cart(self, user_id: str, product_id: int, quantity: int = 1) -> bool:
        with get_db() as db:
            if product_id not in db['products']:
                return False
            cart = db['carts'].get(user_id, Cart())
            for item in cart.items:
                if item.product_id == product_id:
                    item.quantity += quantity
                    db['carts'][user_id] = cart
                    db.sync()
                    return True
            cart.items.append(CartItem(product_id=product_id, quantity=quantity))
            db['carts'][user_id] = cart
            db.sync()
            return True

    def remove_from_cart(self, user_id: str, product_id: int) -> bool:
        with get_db() as db:
            cart = db['carts'].get(user_id, Cart())
            cart.items = [item for item in cart.items if item.product_id != product_id]
            db['carts'][user_id] = cart
            db.sync()
            return True

    def checkout(self, user_id: str) -> Optional[Order]:
        with get_db() as db:
            cart = db['carts'].get(user_id, Cart())
            if not cart.items:
                return None
            order_items = []
            total = 0.0
            for cart_item in cart.items:
                product = db['products'].get(cart_item.product_id)
                if product:
                    order_item = OrderItem(
                        product_id=product.id,
                        name=product.name,
                        price=product.price,
                        quantity=cart_item.quantity
                    )
                    order_items.append(order_item)
                    total += product.price * cart_item.quantity
            oid = db['next_order_id']
            order = Order(
                id=oid,
                items=order_items,
                total=total,
                created_at=datetime.now(),
                paid=True
            )
            db['orders'][oid] = order
            db['next_order_id'] += 1
            cart.items = []
            db['carts'][user_id] = cart
            db.sync()
            return order

    def get_order(self, order_id: int) -> Optional[Order]:
        with get_db() as db:
            return db['orders'].get(order_id)


store = MemoryStore()
