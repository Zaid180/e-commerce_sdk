import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sdk'))

from sdk.ecommerce_sdk import EcommerceSDK


def print_separator(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")


def print_json(data, title=""):
    if title:
        print(f"\n{title}:")
    import json
    print(json.dumps(data, indent=2, default=str))


def main():
    print_separator("E-commerce System Demo")
    
    sdk = EcommerceSDK()
    
    try:
        health = sdk.health_check()
        print(f"✓ Backend is running: {health['message']}")
    except Exception as e:
        print(f"✗ Backend connection failed: {e}")
        print("Please start the backend server first!")
        return
    
    print_separator("1. SELLER: Adding Products")
    
    products = [
        {"name": "Laptop", "price": 74999.99, "description": "High-performance laptop"},
        {"name": "Mouse", "price": 2249.99, "description": "Wireless optical mouse"},
        {"name": "Keyboard", "price": 5999.99, "description": "Mechanical gaming keyboard"},
        {"name": "Monitor", "price": 22499.99, "description": "27-inch 4K monitor"}
    ]
    
    added_products = []
    for product_data in products:
        product = sdk.add_product(**product_data)
        added_products.append(product)
        print(f"✓ Added: {product['name']} - ₹{product['price']}")
    
    print_separator("2. SELLER: Listing All Products")
    all_products = sdk.get_products()
    print(f"Total products in store: {len(all_products)}")
    for product in all_products:
        print(f"  - {product['name']}: ₹{product['price']} (ID: {product['id']})")
    
    print_separator("3. SELLER: Updating a Product")
    updated_product = sdk.update_product(1, price=67499.99, description="Updated: High-performance laptop with discount")
    print(f"✓ Updated product: {updated_product['name']} - New price: ₹{updated_product['price']}")
    
    print_separator("4. BUYER: Viewing Available Products")
    available_products = sdk.get_products()
    print("Available products for purchase:")
    for product in available_products:
        print(f"  - {product['name']}: ₹{product['price']} - {product['description']}")
    
    print_separator("5. BUYER: Adding Items to Cart")
    
    cart_items = [
        (1, 1),  # 1 Laptop
        (2, 2),  # 2 Mice
        (3, 1),  # 1 Keyboard
        (4, 1)   # 1 Monitor
    ]
    
    for product_id, quantity in cart_items:
        result = sdk.add_to_cart(product_id, quantity)
        product = sdk.get_product(product_id)
        print(f"✓ Added {quantity}x {product['name']} to cart")
    
    print_separator("6. BUYER: Viewing Cart")
    cart = sdk.view_cart()
    print(f"Cart contains {len(cart['items'])} different products:")
    total_items = 0
    cart_total = 0.0
    
    for item in cart['items']:
        product = sdk.get_product(item['product_id'])
        item_total = product['price'] * item['quantity']
        cart_total += item_total
        total_items += item['quantity']
        print(f"  - {product['name']}: {item['quantity']}x ₹{product['price']} = ₹{item_total:.2f}")
    
    print(f"\nCart Summary: {total_items} items, Total: ₹{cart_total:.2f}")
    
    print_separator("7. BUYER: Removing One Item from Cart")
    removed_item = sdk.remove_from_cart(2)
    print("✓ Removed Mouse from cart")
    
    updated_cart = sdk.view_cart()
    print(f"Updated cart now contains {len(updated_cart['items'])} different products:")
    for item in updated_cart['items']:
        product = sdk.get_product(item['product_id'])
        print(f"  - {product['name']}: {item['quantity']}x ₹{product['price']}")
    
    print_separator("8. BUYER: Checkout - Creating Order")
    order = sdk.checkout()
    
    print("✓ Order created successfully!")
    print(f"Order ID: {order['id']}")
    print(f"Order Date: {order['created_at']}")
    print(f"Total Amount: ₹{order['total']:.2f}")
    
    print("\nOrder Items:")
    for item in order['items']:
        print(f"  - {item['name']}: {item['quantity']}x ₹{item['price']} = ₹{item['price'] * item['quantity']:.2f}")
    
    print_separator("9. BUYER: Verifying Empty Cart")
    final_cart = sdk.view_cart()
    print(f"Cart is now empty: {len(final_cart['items'])} items")
    
    print_separator("10. SELLER: Deleting a Product")
    deleted = sdk.delete_product(4)
    print("✓ Deleted Monitor from store")
    
    remaining_products = sdk.get_products()
    print(f"Remaining products in store: {len(remaining_products)}")
    for product in remaining_products:
        print(f"  - {product['name']}: ₹{product['price']}")
    
    print_separator("Demo Completed Successfully!")
    print("All e-commerce operations have been demonstrated:")
    print("✓ Product management (CRUD)")
    print("✓ Cart operations (add, view, remove)")
    print("✓ Order creation and checkout")
    print("✓ Full buyer and seller workflows")


if __name__ == "__main__":
    main()
