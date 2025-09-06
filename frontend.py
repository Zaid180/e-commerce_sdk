"""
Streamlit Frontend for Minimal E-commerce System
- Uses only the SDK to interact with the backend API
- Allows buyer and seller flows (add/list/update/delete products, cart, checkout)
- Clean, minimal UI
"""
import streamlit as st
import requests
from sdk.ecommerce_sdk import EcommerceSDK

st.set_page_config(page_title="EchoCart", layout="centered")


# --- Auth State ---
if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'sdk' not in st.session_state:
    st.session_state['sdk'] = EcommerceSDK()
if 'auth_message' not in st.session_state:
    st.session_state['auth_message'] = None
if 'auth_message_type' not in st.session_state:
    st.session_state['auth_message_type'] = None
if 'show_success_toast' not in st.session_state:
    st.session_state['show_success_toast'] = False
sdk = st.session_state['sdk']
if st.session_state['token']:
    sdk.set_token(st.session_state['token'])


# Helper handlers for cart actions using new API endpoints
def _increase_quantity(pid: int):
    sdk = st.session_state.get('sdk')
    try:
        sdk.increase_cart_quantity(pid)
        st.session_state['cart_refresh'] = True
    except Exception as e:
        st.error(f"Failed to increase quantity: {e}")

def _decrease_quantity(pid: int):
    sdk = st.session_state.get('sdk')
    try:
        sdk.decrease_cart_quantity(pid)
        st.session_state['cart_refresh'] = True
    except Exception as e:
        st.error(f"Failed to decrease quantity: {e}")

def _remove_item(pid: int):
    sdk = st.session_state.get('sdk')
    try:
        sdk.remove_from_cart(pid)
        st.session_state['cart_refresh'] = True
    except Exception as e:
        st.error(f"Failed to remove item: {e}")


st.markdown("""
<style>
.main {background: linear-gradient(135deg, #5a6c7d 0%, #6c5b7b 100%); min-height: 100vh;}
.stButton>button {
    background: #8b0000;
    color: white;
    border-radius: 25px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(139, 0, 0, 0.15);
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(139, 0, 0, 0.2);
}
.stTextInput>div>input, .stTextArea>div>textarea, .stNumberInput>div>input {
    border-radius: 15px;
    border: 2px solid #d3d9de;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
}
.cart-item {
    background: #f8f8ff;
    padding: 20px;
    border-radius: 20px;
    border: 1px solid #e6e6fa;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.product-card {
    background: #f8f8ff;
    padding: 20px;
    border-radius: 20px;
    border: 1px solid #e6e6fa;
    margin: 15px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.cart-separator {
    width: 60%;
    margin: 30px auto;
    border-top: 4px solid #8b0000;
    border-radius: 2px;
}
.quantity-btn {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    font-size: 20px;
    font-weight: bold;
    background: linear-gradient(45deg, #708090, #5f9ea0);
    color: white;
    border: none;
    box-shadow: 0 4px 15px rgba(112, 128, 144, 0.2);
}
/* Hide pin icons next to headings */
.stMarkdown h1 > .stButton,
.stMarkdown h2 > .stButton,
.stMarkdown h3 > .stButton,
.stMarkdown h4 > .stButton,
.stMarkdown h5 > .stButton,
.stMarkdown h6 > .stButton,
[data-testid="stMarkdownContainer"] button {
    display: none !important;
}
.element-container button[kind="header"] {
    display: none !important;
}
/* Hide file change and rerun notifications but keep toasts */
[data-testid="stNotificationContentInfo"],
[data-testid="stNotificationContentWarning"],
[data-testid="stStatusWidget"],
.StatusWidget,
[class*="fileChangeNotification"],
[class*="rerunNotification"],
.element-container:has([data-testid="stNotificationContentInfo"]) {
    display: none !important;
}
/* Hide Deploy button and three-dot menu */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton,
[data-testid="stHeader"] > div:last-child,
.stApp > header,
[data-testid="stAppViewContainer"] > .main .block-container > div:first-child > div:last-child,
[class*="viewerBadge"],
[data-testid="manage-app-button"] {
    display: none !important;
}
/* Top center toast notifications */
[data-testid="stToast"] {
    position: fixed !important;
    top: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    z-index: 9999 !important;
    min-width: 300px !important;
    text-align: center !important;
}
.stToast > div {
    margin: 0 auto !important;
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🛒 EchoCart")
st.markdown("*Welcome to EchoCart – your one-stop destination for everything you love, bringing the world right to your fingertips.*")

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
                        # Server sent 200 - Login successful
                        st.session_state['token'] = resp['token']
                        st.session_state['role'] = resp['role']
                        st.session_state['username'] = resp['username']
                        sdk.set_token(resp['token'])
                        st.session_state['show_success_toast'] = True
                        st.rerun()
                    else:
                        sdk.signup(username, password, role)
                        st.toast("Signup successful! Please login.", icon="✅")
                        st.session_state['auth_message'] = None
                        st.session_state['auth_message_type'] = None
                except Exception as e:
                    # Handle all exceptions and show error
                    error_str = str(e)
                    print(f"Login error: {type(e).__name__}: {e}")  # Debug
                    
                    if "401" in error_str or "Unauthorized" in error_str:
                        # st.error("❌ Invalid login credentials!")
                        st.toast("Invalid login credentials!", icon="⚠️")
                    elif "400" in error_str or "already exists" in error_str:
                        # st.error("❌ Username already exists!")
                        st.toast("Username taken!", icon="⚠️")
                    else:
                        # st.error(f"❌ Login failed: {error_str}")
                        st.toast("Login failed!", icon="⚠️")
        # Toast notifications with fallback error messages
        menu = None
    else:
        # Show success toast after login
        if st.session_state.get('show_success_toast', False):
            st.toast("Login successful!", icon="✅")
            st.session_state['show_success_toast'] = False
        
        st.write(f"👤 {st.session_state['username']} ({st.session_state['role']})")
        if st.button("Logout"):
            st.session_state['token'] = None
            st.session_state['role'] = None
            st.session_state['username'] = None
            sdk.set_token(None)
            st.rerun()
        menu = st.session_state.get('role', 'buyer') or 'buyer'
        menu = menu.capitalize()



# Seller View: product management
if menu == "Seller" and st.session_state['role'] == 'seller':
    st.header("Seller Dashboard")
    st.subheader("Add Product") 
    with st.form("add_product_form"):
        name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0.01, step=0.01)
        quantity = st.number_input("Quantity", min_value=0, step=1)
        description = st.text_area("Description")
        submitted = st.form_submit_button("Add Product")
        if submitted and name and price:
            try:
                product = sdk.add_product(name, price, description, quantity=quantity)
                st.success(f"Added: {product['name']} (₹{product['price']}) (Qty: {product.get('quantity', 0)})")
            except Exception as e:
                st.error(f"Error: {e}")

    st.subheader("All Products")
    try:
        products = sdk.get_products()
        for p in products:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            st.markdown(f"### {p['name']}")
            st.write(f"**Price:** ₹{p['price']:.2f}")
            st.write(f"**Description:** {p['description']}")
            st.write(f"**Stock:** {p.get('quantity', 0)} available")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✏️ Update", key=f"update_{p['id']}"):
                    st.session_state['update_id'] = p['id']
            with col2:
                if st.button(f"🗑️ Delete", key=f"delete_{p['id']}"):
                    try:
                        sdk.delete_product(p['id'])
                        st.success(f"Deleted {p['name']}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

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


# Buyer View: product browsing and cart
if menu == "Buyer" and st.session_state['role'] == 'buyer':
    st.header("Buyer Shop")
    
    # Enhanced search section
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 **Find Your Products**")
    search_query = st.text_input(
        "Search Products",
        placeholder="🔍 Search products by name or description...",
        key="search",
        help="Type to search for products instantly",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.markdown(f"### {p['name']}")
        st.write(f"**Price:** ₹{p['price']:.2f}")
        st.write(f"**Description:** {p['description']}")
        st.write(f"**Stock:** {p.get('quantity', 0)} available")
        if st.button(f"🛒 Add to Cart", key=f"add_{p['id']}"):
            if p.get('quantity', 0) <= 0:
                st.toast(f"{p['name']} is out of stock!", icon="⚠️")
            else:
                try:
                    sdk.add_to_cart(p['id'])
                    st.toast(f"Added {p['name']} to cart", icon="✅")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Cart separator
    st.markdown('<hr class="cart-separator">', unsafe_allow_html=True)
    st.markdown("## 🛒 **YOUR SHOPPING CART**")
    
    # Check if cart needs refresh
    if st.session_state.get('cart_refresh', False):
        st.session_state['cart_refresh'] = False
        st.rerun()
    
    try:
        cart = sdk.view_cart()
        products_for_cart = sdk.get_products()
        
        if cart and cart.get('items'):
            total_amount = 0
            
            for item in cart['items']:
                prod = next((x for x in products_for_cart if x['id']==item['product_id']), None)
                if prod:
                    item_total = item['quantity'] * prod['price']
                    total_amount += item_total
                    
                    # Cart item card
                    st.markdown(f'<div class="cart-item">', unsafe_allow_html=True)
                    
                    # Product info row
                    st.markdown(f"### {prod['name']}")
                    st.write(f"Price: **₹{prod['price']:.2f}** per item")
                    
                    # Quantity and controls row
                    col1, col2, col3, col4, col5 = st.columns([0.5, 0.5, 0.5, 1.5, 2])
                    
                    with col1:
                        if st.button("➖", key=f"dec_{prod['id']}", help="Decrease quantity"):
                            if item['quantity'] <= 1:
                                st.toast("Quantity cannot be zero! Use remove button to delete item.", icon="⚠️")
                            else:
                                try:
                                    sdk.decrease_cart_quantity(prod['id'])
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                    
                    with col2:
                        st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold; padding: 8px;'>{item['quantity']}</div>", unsafe_allow_html=True)
                    
                    with col3:
                        if st.button("➕", key=f"inc_{prod['id']}", help="Increase quantity"):
                            if item['quantity'] >= prod.get('quantity', 0):
                                st.toast(f"{prod['name']} is sold out! No more stock available.", icon="⚠️")
                            else:
                                try:
                                    sdk.increase_cart_quantity(prod['id'])
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                    
                    with col4:
                        st.write(f"**Total: ₹{item_total:.2f}**")
                    
                    with col5:
                        if st.button("🗑️ Remove", key=f"rem_{prod['id']}", help="Remove from cart"):
                            try:
                                sdk.remove_from_cart(prod['id'])
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Total and checkout
            st.markdown('<hr class="cart-separator">', unsafe_allow_html=True)
            st.markdown(f"## 🛒 Cart Total: ₹{total_amount:.2f}")
            
            if st.button("🛍️ Buy Now", type="primary", use_container_width=True):
                try:
                    order = sdk.checkout()
                    st.success(f"✅ Order placed successfully! Total: ₹{order['total']:.2f}")
                except Exception as e:
                    st.error(f"❌ Checkout failed: {e}")
        else:
            st.info("🛒 Your cart is empty. Add some products to get started!")
    except Exception as e:
        st.error(f"Error loading cart: {e}")
elif menu == "Buyer":
    st.warning("Please login as a buyer to access the Buyer Shop.")
