"""
Streamlit Frontend for Minimal E-commerce System
- Uses only the SDK to interact with the backend API
- Allows buyer and seller flows (add/list/update/delete products, cart, checkout)
- Clean, minimal UI
"""

import streamlit as st
from sdk.ecommerce_sdk import EcommerceSDK

st.set_page_config(page_title="Minimal E-commerce", layout="centered")


# --- Auth State ---
if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'sdk' not in st.session_state:
    st.session_state['sdk'] = EcommerceSDK()
sdk = st.session_state['sdk']
if st.session_state['token']:
    sdk.set_token(st.session_state['token'])

st.markdown("""
<style>
.main {background-color: #f8f9fa;}
.stButton>button {background-color: #4CAF50; color: white; border-radius: 5px;}
.stTextInput>div>input {border-radius: 5px;}
.stTextArea>div>textarea {border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

st.title("🛒 Minimal E-commerce System")

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shopping-cart-loaded.png", width=80)
    if not st.session_state['token']:
        st.subheader("Login or Signup")
        auth_tab = st.radio("Select", ["Login", "Signup"])
        with st.form("auth_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if auth_tab == "Signup":
                role = st.selectbox("Role", ["buyer", "seller"])
            submitted = st.form_submit_button(auth_tab)
            if submitted and username and password:
                try:
                    if auth_tab == "Login":
                        resp = sdk.login(username, password)
                        st.session_state['token'] = resp['token']
                        st.session_state['role'] = resp['role']
                        st.session_state['username'] = resp['username']
                        sdk.set_token(resp['token'])
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        sdk.signup(username, password, role)
                        st.success("Signup successful! Please login.")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.write(f"👤 {st.session_state['username']} ({st.session_state['role']})")
        if st.button("Logout"):
            st.session_state['token'] = None
            st.session_state['role'] = None
            st.session_state['username'] = None
            sdk.set_token(None)
            st.experimental_rerun()
    menu = st.radio("Select Role", ["Buyer", "Seller"])


# Seller View
if menu == "Seller" and st.session_state['role'] == 'seller':
    st.header("Seller Dashboard")
    st.subheader("Add Product")
    with st.form("add_product_form"):
        name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0.01, step=0.01)
        description = st.text_area("Description")
        submitted = st.form_submit_button("Add Product")
        if submitted and name and price:
            try:
                product = sdk.add_product(name, price, description)
                st.success(f"Added: {product['name']} (${product['price']})")
            except Exception as e:
                st.error(f"Error: {e}")

    st.subheader("All Products")
    try:
        products = sdk.get_products()
        for p in products:
            st.write(f"**{p['name']}** (${p['price']}) - {p['description']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Update {p['id']}"):
                    st.session_state['update_id'] = p['id']
            with col2:
                if st.button(f"Delete {p['id']}"):
                    try:
                        sdk.delete_product(p['id'])
                        st.success(f"Deleted {p['name']}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        # Update form
        if 'update_id' in st.session_state:
            pid = st.session_state['update_id']
            st.subheader(f"Update Product ID {pid}")
            prod = next((x for x in products if x['id']==pid), None)
            if prod:
                with st.form("update_product_form"):
                    name = st.text_input("Name", value=prod['name'])
                    price = st.number_input("Price", value=prod['price'], min_value=0.01, step=0.01)
                    description = st.text_area("Description", value=prod['description'])
                    submitted = st.form_submit_button("Update")
                    if submitted:
                        try:
                            sdk.update_product(pid, name=name, price=price, description=description)
                            st.success("Product updated!")
                            del st.session_state['update_id']
                        except Exception as e:
                            st.error(f"Error: {e}")
    except Exception as e:
        st.error(f"Error: {e}")
elif menu == "Seller":
    st.warning("Please login as a seller to access the Seller Dashboard.")


# Buyer View
if menu == "Buyer" and st.session_state['role'] == 'buyer':
    st.header("Buyer Shop")
    st.subheader("Search Products")
    search_query = st.text_input("Search by name or description", key="search")
    if search_query:
        try:
            products = sdk.search_products(search_query)
        except Exception as e:
            st.error(f"Error: {e}")
            products = []
    else:
        try:
            products = sdk.get_products()
        except Exception as e:
            st.error(f"Error: {e}")
            products = []
    st.subheader("Available Products")
    for p in products:
        st.write(f"**{p['name']}** (${p['price']}) - {p['description']}")
        if st.button(f"Add to Cart {p['id']}"):
            try:
                sdk.add_to_cart(p['id'])
                st.success(f"Added {p['name']} to cart")
            except Exception as e:
                st.error(f"Error: {e}")
    st.subheader("Your Cart")
    try:
        cart = sdk.view_cart()
        if cart['items']:
            for item in cart['items']:
                prod = next((x for x in products if x['id']==item['product_id']), None)
                if prod:
                    st.write(f"{prod['name']}: {item['quantity']} x ${prod['price']}")
                    if st.button(f"Remove {prod['id']}"):
                        try:
                            sdk.remove_from_cart(prod['id'])
                            st.success(f"Removed {prod['name']} from cart")
                        except Exception as e:
                            st.error(f"Error: {e}")
            if st.button("Checkout"):
                try:
                    order = sdk.checkout()
                    st.success(f"Order placed! Total: ${order['total']}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Your cart is empty.")
    except Exception as e:
        st.error(f"Error: {e}")
elif menu == "Buyer":
    st.warning("Please login as a buyer to access the Buyer Shop.")
