from typing import Dict, List, Optional
from datetime import datetime
import secrets
from .models import Product, Cart, Order, OrderItem, User, SessionToken, CartItem
from .db_store import get_db


class MemoryStore:
    def __init__(self):
        # initialize missing keys safely
        with get_db() as db:
            for key, default in (
                ("products", {}),
                ("carts", {}),
                ("orders", {}),
                ("users", {}),
                ("sessions", {}),
            ):
                try:
                    # accessing may raise during unpickle; if so, reset
                    _ = db.get(key, default)
                except Exception:
                    db[key] = default
            if 'next_product_id' not in db:
                db['next_product_id'] = 1
            if 'next_order_id' not in db:
                db['next_order_id'] = 1

    def _safe_get(self, db, key, default):
        try:
            val = db.get(key, default)
            # if stored value is a Pydantic model (old data), try to convert to primitive
            return val
        except Exception:
            # corrupted/unpicklable entry: reset to default and return default
            db[key] = default
            db.sync()
            return default

    def _to_user_dict(self, user_obj):
        if user_obj is None:
            return None
        if isinstance(user_obj, dict):
            return user_obj
        # pydantic model instance
        if hasattr(user_obj, 'username'):
            return {"username": getattr(user_obj, 'username', None),
                    "password": getattr(user_obj, 'password', None),
                    "role": getattr(user_obj, 'role', None)}
        return None

    def _to_session_dict(self, sess_obj):
        if sess_obj is None:
            return None
        if isinstance(sess_obj, dict):
            return sess_obj
        if hasattr(sess_obj, 'token'):
            return {"token": getattr(sess_obj, 'token', None),
                    "username": getattr(sess_obj, 'username', None),
                    "role": getattr(sess_obj, 'role', None)}
        return None

    def _to_product_dict(self, prod_obj):
        if prod_obj is None:
            return None
        if isinstance(prod_obj, dict):
            return prod_obj
        # pydantic Product model - use model_dump() or dict() method
        if hasattr(prod_obj, 'model_dump'):
            return prod_obj.model_dump()
        elif hasattr(prod_obj, 'dict'):
            return prod_obj.dict()
        elif hasattr(prod_obj, 'id'):
            # fallback to attribute access
            return {"id": getattr(prod_obj, 'id', None),
                    "name": getattr(prod_obj, 'name', ''),
                    "price": getattr(prod_obj, 'price', 0.0),
                    "description": getattr(prod_obj, 'description', ''),
                    "quantity": getattr(prod_obj, 'quantity', 0)}
        return None

    def _to_cart_dict(self, cart_obj):
        if cart_obj is None:
            return {"items": []}
        if isinstance(cart_obj, dict):
            # ensure items list of dicts
            items = []
            for it in cart_obj.get('items', []):
                if isinstance(it, dict):
                    items.append({"product_id": it.get('product_id'), "quantity": it.get('quantity', 0)})
                else:
                    # maybe CartItem pydantic
                    items.append({"product_id": getattr(it, 'product_id', None), "quantity": getattr(it, 'quantity', 0)})
            return {"items": items}
        # pydantic Cart instance
        if hasattr(cart_obj, 'items'):
            items = []
            for it in getattr(cart_obj, 'items', []):
                if isinstance(it, dict):
                    items.append({"product_id": it.get('product_id'), "quantity": it.get('quantity', 0)})
                else:
                    items.append({"product_id": getattr(it, 'product_id', None), "quantity": getattr(it, 'quantity', 0)})
            return {"items": items}
        return {"items": []}

    def search_products(self, query: str):
        q = query.lower()
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if not isinstance(products, dict):
                # reset corrupted products map
                products = {}
                db['products'] = products
                db.sync()
            # products are stored as dicts keyed by id
            result = []
            for p in products.values():
                prod_dict = self._to_product_dict(p)
                if prod_dict and (q in prod_dict['name'].lower() or q in prod_dict['description'].lower()):
                    # Ensure all required fields exist
                    if 'quantity' not in prod_dict:
                        prod_dict['quantity'] = 0
                    result.append(Product(**prod_dict))
            return result

    def signup(self, username: str, password: str, role: str) -> bool:
        with get_db() as db:
            users = self._safe_get(db, 'users', {})
            if username in users:
                return False
            users[username] = {"username": username, "password": password, "role": role}
            db['users'] = users
            db.sync()
            return True

    def login(self, username: str, password: str) -> Optional[SessionToken]:
        with get_db() as db:
            users = self._safe_get(db, 'users', {})
            raw_user = users.get(username)
            user = self._to_user_dict(raw_user)
            if not user or user.get('password') != password:
                return None
            token = secrets.token_hex(16)
            sessions = self._safe_get(db, 'sessions', {})
            sessions[token] = {"token": token, "username": username, "role": user.get('role')}
            db['sessions'] = sessions
            db.sync()
            return SessionToken(**sessions[token])

    def get_user_by_token(self, token: str) -> Optional[User]:
        with get_db() as db:
            sessions = self._safe_get(db, 'sessions', {})
            raw_session = sessions.get(token)
            session = self._to_session_dict(raw_session)
            if not session:
                return None
            users = self._safe_get(db, 'users', {})
            raw_user = users.get(session.get('username'))
            user = self._to_user_dict(raw_user)
            if not user:
                return None
            return User(**user)

    def add_product(self, name: str, price: float, description: str, quantity: int = 0) -> Product:
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if not isinstance(products, dict):
                products = {}
                db['products'] = products
                db.sync()
            pid = db.get('next_product_id', 1)
            product = {"id": pid, "name": name, "price": price, "description": description, "quantity": quantity}
            products[pid] = product
            db['products'] = products
            db['next_product_id'] = pid + 1
            db.sync()
            return Product(**product)

    def get_product(self, product_id: int) -> Optional[Product]:
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if not isinstance(products, dict):
                products = {}
                db['products'] = products
                db.sync()
            raw = products.get(product_id)
            p = self._to_product_dict(raw)
            if p:
                # Ensure all required fields exist
                if 'quantity' not in p:
                    p['quantity'] = 0
                return Product(**p)
            return None

    def get_all_products(self) -> List[Product]:
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if not isinstance(products, dict):
                products = {}
                db['products'] = products
                db.sync()
            out = []
            for raw in products.values():
                p = self._to_product_dict(raw)
                if p:
                    # Ensure all required fields exist
                    if 'quantity' not in p:
                        p['quantity'] = 0
                    out.append(Product(**p))
            return out

    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if not isinstance(products, dict):
                products = {}
                db['products'] = products
                db.sync()
            if product_id not in products:
                return None
            raw = products[product_id]
            prod = self._to_product_dict(raw) or raw
            # Ensure quantity field exists
            if 'quantity' not in prod:
                prod['quantity'] = 0
            for key, value in kwargs.items():
                if value is not None:
                    prod[key] = value
            products[product_id] = prod
            db['products'] = products
            db.sync()
            return Product(**prod)

    def delete_product(self, product_id: int) -> bool:
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if not isinstance(products, dict):
                products = {}
                db['products'] = products
                db.sync()
            if product_id in products:
                del products[product_id]
                db['products'] = products
                db.sync()
                return True
            return False

    def get_cart(self, user_id: str) -> Cart:
        with get_db() as db:
            carts = self._safe_get(db, 'carts', {})
            raw = carts.get(user_id, {"items": []})
            cart = self._to_cart_dict(raw)
            items = [CartItem(**it) for it in cart.get('items', [])]
            return Cart(items=items)

    def add_to_cart(self, user_id: str, product_id: int, quantity: int = 1) -> bool:
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if product_id not in products:
                return False
            carts = self._safe_get(db, 'carts', {})
            raw = carts.get(user_id, {"items": []})
            cart = self._to_cart_dict(raw)
            for it in cart['items']:
                if it['product_id'] == product_id:
                    it['quantity'] += quantity
                    carts[user_id] = cart
                    db['carts'] = carts
                    db.sync()
                    return True
            cart['items'].append({"product_id": product_id, "quantity": quantity})
            carts[user_id] = cart
            db['carts'] = carts
            db.sync()
            return True

    def remove_from_cart(self, user_id: str, product_id: int) -> bool:
        with get_db() as db:
            carts = self._safe_get(db, 'carts', {})
            raw = carts.get(user_id, {"items": []})
            cart = self._to_cart_dict(raw)
            cart['items'] = [item for item in cart.get('items', []) if item['product_id'] != product_id]
            carts[user_id] = cart
            db['carts'] = carts
            db.sync()
            return True

    def increase_cart_quantity(self, user_id: str, product_id: int) -> bool:
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if product_id not in products:
                return False
            carts = self._safe_get(db, 'carts', {})
            raw = carts.get(user_id, {"items": []})
            cart = self._to_cart_dict(raw)
            for item in cart['items']:
                if item['product_id'] == product_id:
                    item['quantity'] += 1
                    carts[user_id] = cart
                    db['carts'] = carts
                    db.sync()
                    return True
            return False

    def decrease_cart_quantity(self, user_id: str, product_id: int) -> bool:
        with get_db() as db:
            products = self._safe_get(db, 'products', {})
            if product_id not in products:
                return False
            carts = self._safe_get(db, 'carts', {})
            raw = carts.get(user_id, {"items": []})
            cart = self._to_cart_dict(raw)
            for item in cart['items']:
                if item['product_id'] == product_id:
                    if item['quantity'] > 1:
                        item['quantity'] -= 1
                    else:
                        # Remove item if quantity becomes 0
                        cart['items'] = [i for i in cart['items'] if i['product_id'] != product_id]
                    carts[user_id] = cart
                    db['carts'] = carts
                    db.sync()
                    return True
            return False

    def checkout(self, user_id: str) -> Optional[Order]:
        with get_db() as db:
            # Get cart
            carts = self._safe_get(db, 'carts', {})
            raw_cart = carts.get(user_id, {"items": []})
            cart = self._to_cart_dict(raw_cart)
            
            if not cart.get('items'):
                return None
            
            # Get products and orders
            products = self._safe_get(db, 'products', {})
            orders = self._safe_get(db, 'orders', {})
            
            order_items = []
            total = 0.0
            
            for cart_item in cart.get('items', []):
                product_id = cart_item['product_id']
                raw_product = products.get(product_id)
                
                if raw_product:
                    product = self._to_product_dict(raw_product)
                    if product:
                        order_item = {
                            "product_id": product['id'],
                            "name": product['name'],
                            "price": product['price'],
                            "quantity": cart_item['quantity']
                        }
                        order_items.append(order_item)
                        total += product['price'] * cart_item['quantity']
            
            if not order_items:
                return None
            
            # Create order
            order_id = db.get('next_order_id', 1)
            order_data = {
                "id": order_id,
                "items": order_items,
                "total": total,
                "created_at": datetime.now(),
                "paid": True
            }
            
            orders[order_id] = order_data
            db['orders'] = orders
            db['next_order_id'] = order_id + 1
            
            # Clear cart
            carts[user_id] = {"items": []}
            db['carts'] = carts
            db.sync()
            
            # Return Order model
            order_items_models = [OrderItem(**item) for item in order_items]
            return Order(
                id=order_id,
                items=order_items_models,
                total=total,
                created_at=order_data['created_at'],
                paid=True
            )

    def get_order(self, order_id: int) -> Optional[Order]:
        with get_db() as db:
            orders = self._safe_get(db, 'orders', {})
            o = orders.get(order_id)
            return Order(**o) if o else None


store = MemoryStore()
