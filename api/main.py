# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client["order_management"]

# Helper function to convert ObjectId to string
def to_dict(document):
    document["_id"] = str(document["_id"])
    return document

# Define Pydantic models for validation
class Customer(BaseModel):
    name: str
    email: str
    address: str

class Product(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    customer_id: str
    items: List[OrderItem]

# CRUD Endpoints for Customers
@app.post("/customers/")
def create_customer(customer: Customer):
    customer_id = db.customers.insert_one(customer.dict()).inserted_id
    return {"customer_id": str(customer_id)}

@app.get("/customers/{customer_id}")
def read_customer(customer_id: str):
    customer = db.customers.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return to_dict(customer)

@app.put("/customers/{customer_id}")
def update_customer(customer_id: str, customer: Customer):
    result = db.customers.update_one(
        {"_id": ObjectId(customer_id)}, {"$set": customer.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer updated successfully"}

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: str):
    result = db.customers.delete_one({"_id": ObjectId(customer_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

# CRUD Endpoints for Products
@app.post("/products/")
def create_product(product: Product):
    product_id = db.products.insert_one(product.dict()).inserted_id
    return {"product_id": str(product_id)}

@app.get("/products/{product_id}")
def read_product(product_id: str):
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return to_dict(product)

@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    result = db.products.update_one(
        {"_id": ObjectId(product_id)}, {"$set": product.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    result = db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# CRUD Endpoints for Orders
@app.post("/orders/")
def create_order(order: Order):
    # Verify customer exists
    if not db.customers.find_one({"_id": ObjectId(order.customer_id)}):
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify each product exists
    for item in order.items:
        if not db.products.find_one({"_id": ObjectId(item.product_id)}):
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")

    order_id = db.orders.insert_one(order.dict()).inserted_id
    return {"order_id": str(order_id)}

@app.get("/orders/{order_id}")
def read_order(order_id: str):
    order = db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return to_dict(order)

@app.put("/orders/{order_id}")
def update_order(order_id: str, order: Order):
    # Verify customer exists
    if not db.customers.find_one({"_id": ObjectId(order.customer_id)}):
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify each product exists
    for item in order.items:
        if not db.products.find_one({"_id": ObjectId(item.product_id)}):
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")

    result = db.orders.update_one(
        {"_id": ObjectId(order_id)}, {"$set": order.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order updated successfully"}

@app.delete("/orders/{order_id}")
def delete_order(order_id: str):
    result = db.orders.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}
