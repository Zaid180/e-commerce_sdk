import requests
from typing import List, Dict, Any, Optional



class EcommerceSDK:
    def __init__(self, base_url: str = "http://localhost:8001", user_id: str = "default_user", token: str = None):
        self.base_url = base_url.rstrip('/')
        self.user_id = user_id
        self.token = token
        self.session = requests.Session()

    def set_token(self, token: str):
        self.token = token

    def _headers(self):
        return {"token": self.token} if self.token else {}
   # add product function 
    def add_product(self, name: str, price: float, description: str, quantity: int = 0) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/products",
            json={"name": name, "price": price, "description": description, "quantity": quantity},
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def update_product(self, product_id: int, **kwargs) -> Dict[str, Any]:
        response = self.session.put(
            f"{self.base_url}/products/{product_id}",
            json=kwargs,
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def delete_product(self, product_id: int) -> Dict[str, Any]:
        response = self.session.delete(f"{self.base_url}/products/{product_id}", headers=self._headers())
        response.raise_for_status()
        return response.json()
    
   # get all products

    def get_products(self) -> List[Dict[str, Any]]:
        response = self.session.get(f"{self.base_url}/products", headers=self._headers())
        response.raise_for_status()
        return response.json()

    def search_products(self, query: str) -> List[Dict[str, Any]]:
        response = self.session.get(f"{self.base_url}/products/search", params={"query": query}, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def get_product(self, product_id: int) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}/products/{product_id}", headers=self._headers())
        response.raise_for_status()
        return response.json()

    def add_to_cart(self, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/cart",
            params={"product_id": product_id, "quantity": quantity},
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def view_cart(self) -> Dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/cart",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def remove_from_cart(self, product_id: int) -> Dict[str, Any]:
        response = self.session.delete(
            f"{self.base_url}/cart/{product_id}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def increase_cart_quantity(self, product_id: int) -> Dict[str, Any]:
        response = self.session.put(
            f"{self.base_url}/cart/{product_id}/increase",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def decrease_cart_quantity(self, product_id: int) -> Dict[str, Any]:
        response = self.session.put(
            f"{self.base_url}/cart/{product_id}/decrease",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def checkout(self) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/checkout",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def signup(self, username: str, password: str, role: str) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/signup",
            json={"username": username, "password": password, "role": role}
        )
        response.raise_for_status()
        return response.json()

    def login(self, username: str, password: str) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()
