# E-commerce System

A minimal Python-only E-commerce system built with FastAPI, featuring in-memory storage, RESTful APIs, and a complete SDK.

## Features

- **FastAPI Backend**: RESTful API with automatic documentation
- **In-Memory Storage**: No database dependencies
- **Python SDK**: Easy integration with the API
- **Complete Demo**: Full buyer/seller workflow demonstration
- **CORS Enabled**: Ready for frontend integration

## Quick Start

1. Create virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Start backend: `python start_server.py` or `python -m backend.main`
5. Run demo: `python demo.py`

## API Endpoints

### Seller APIs
- `POST /products` - Add product
- `GET /products` - List all products
- `GET /products/{id}` - Get product details
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Buyer APIs
- `POST /cart` - Add product to cart
- `GET /cart` - View cart
- `DELETE /cart/{id}` - Remove product from cart
- `POST /checkout` - Checkout (create order)

## Documentation

- `flow.txt` - Detailed development process
- `commands.txt` - Setup and run commands
- API docs available at `http://localhost:8001/docs` when running

## Project Structure

```
ecommerce/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models
│   └── memory_store.py  # In-memory storage
├── sdk/
│   └── ecommerce_sdk.py # Python SDK
├── demo.py              # Demo script
├── flow.txt             # Development flow
├── commands.txt         # Setup commands
└── requirements.txt     # Dependencies
```
