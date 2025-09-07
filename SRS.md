# SRS — EchoCart (Minimal E-commerce)

## 1. Title
EchoCart — Minimal e-commerce demo (Streamlit frontend + FastAPI backend)

## 2. Revision history
- v0.1 — Initial draft — 2025-09-07

## 3. Purpose & Scope
Purpose: specify behavior and constraints for EchoCart so devs/testers know what to build/verify.
Scope: user auth (signup/login), product catalog CRUD (seller), product browsing/search (buyer), cart management, checkout (orders). Local shelve persistence.

## 4. Definitions / Glossary
- Buyer — user with role buyer, can browse, add to cart, checkout.
- Seller — user with role seller, can create/update/delete products.
- SDK — client wrapper used by frontend to call backend endpoints.
- DB — shelve-backed local storage (ecommerce_db).

## 5. System overview
Two-tier app:
- Frontend: Streamlit app `frontend.py` using `sdk/ecommerce_sdk.py`.
- Backend: FastAPI app `backend/main.py` using `backend/memory_store.py` for business logic and `backend/db_store.py` for persistence.

## 6. Stakeholders
- Primary: developers, QA, demo users.
- Secondary: maintainers.

## 7. Functional requirements (FR)
FR1. User signup — POST /signup — store username/password/role. (backend/main.py -> store.signup)
FR2. User login — POST /login — return session token and role. (backend/main.py -> store.login)
FR3. Seller: Create product — POST /products — store product (id,name,price,description,quantity). (backend/main.py -> store.add_product)
FR4. Seller: Read/Update/Delete product — GET/PUT/DELETE /products/{id}. (backend/main.py -> store.*)
FR5. Buyer: List/search products — GET /products, GET /products/search.
FR6. Cart: Add item — POST /cart (user-specific). Add must persist quantity. (memory_store.add_to_cart)
FR7. Cart: View cart — GET /cart returns items with product details/quantity.
FR8. Cart: Increase/decrease/set quantity — endpoints or combination (POST/DELETE or dedicated /cart/{id}/quantity).
FR9. Remove item from cart — DELETE /cart/{product_id}
FR10. Checkout — POST /checkout — create order, validate stock, decrement inventory atomically, clear cart.
FR11. SDK — wrapper methods for all above endpoints; support token header.

Each FR should have acceptance criteria (see section 15).

## 8. Non-functional requirements (NFR)
NFR1. Local persistence (shelve) must store only plain dicts (avoid pickled model objects) to prevent breakage on refactor.
NFR2. Security: passwords stored hashed (recommend bcrypt) — currently plaintext but must be upgraded before production.
NFR3. Concurrency: implement atomic checks/updates on checkout to avoid oversell.
NFR4. Performance: support single-process demo; shelve concurrency not required.
NFR5. Usability: Streamlit UI should update cart quantities inline; hide auth controls when logged in.

## 9. Data model (summary)
- Product: id:int, name:str, price:float, description:str, quantity:int
- User: username:str, password:str (hashed), role: 'buyer'|'seller'
- Cart: user_id -> list[CartItem(product_id:int, quantity:int)]
- Order: id:int, user_id, items:list[OrderItem], total:float, created_at:datetime

## 10. REST API (essential)
- POST /signup
  - Body: {username, password, role}
  - Response: 201 or 400
- POST /login
  - Body: {username, password}
  - Response: {token, username, role} or 401
- POST /products
  - Auth: token (seller)
  - Body: {name, price, description, quantity}
  - Response: product
- GET /products
  - Response: [product]
- GET /products/{id}
- PUT /products/{id}
- DELETE /products/{id}
- GET /products/search?query=
- POST /cart
  - Body: {product_id, quantity}
  - User identified by token or default_user
- GET /cart
- DELETE /cart/{product_id}
- POST /checkout
  - Validates stock, decrements product.quantity, creates order, clears cart.
  - Response: order object

Map endpoints to implementation files:
- backend/main.py — endpoint definitions
- backend/memory_store.py — business logic and DB read/write
- sdk/ecommerce_sdk.py — client wrapper used by frontend.py

## 11. UI Requirements / Flows
- Sidebar: login/signup radio (hidden when logged in). Show username/role and Logout when authenticated.
- Seller dashboard: form to add product; list products with Update/Delete buttons.
- Buyer shop: search, product cards with Add to Cart; Cart section shows items with [-] qty [+] controls, Remove and Buy Now buttons. Each +/- affects only that row.
- Styles: CSS defined in frontend.py via st.markdown style block.

## 12. Security & Privacy
- Use token-based session (backend returns token stored in sessions map).
- Do not store plaintext passwords in production; use hashing.
- Validate tokens on endpoints that require auth (enforce seller role on product create).

## 13. Performance / Scalability
- Single-user/demo use. For production, replace shelve with real DB and add transactions.

## 14. Error handling & logging
- Backend returns proper HTTP status codes (400/401/404/500).
- Log stack traces to console during dev. Frontend should display user-friendly toasts.

## 15. Acceptance criteria / test cases (examples)
- TC1 signup/login: signup new user, login returns token and role; token accepted by /cart and product endpoints.
- TC2 seller add product: POST /products (seller) creates product persisted in DB and visible via GET /products.
- TC3 add-to-cart & quantity: add product to cart, increase/decrease quantity via +/- only affects that item and persists; cart GET returns updated qty.
- TC4 checkout reduces product.quantity; orders created; cart emptied.
- TC5 UI: radio hidden when logged in; reappears after logout.

## 16. Constraints & assumptions
- Local dev environment (Windows), Streamlit/uvicorn running concurrently.
- Shelve DB files created in project root; may need deletion after major model refactors.

## 17. Appendix
- File map:
  - c:\Users\nkaushik\Desktop\Project\frontend.py — UI + CSS
  - c:\Users\nkaushik\Desktop\Project\sdk\ecommerce_sdk.py — client SDK
  - c:\Users\nkaushik\Desktop\Project\backend\main.py — FastAPI app
  - c:\Users\nkaushik\Desktop\Project\backend\memory_store.py — business logic & persistence
  - c:\Users\nkaushik\Desktop\Project\backend\models.py — pydantic models