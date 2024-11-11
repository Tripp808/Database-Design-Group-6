# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from datetime import datetime 


app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client["order_management"]

# Helper function to convert MongoDB document to dictionary with _id as a string
def to_dict(document):
    if "_id" in document:
        document["_id"] = str(document["_id"])
    return document

# Define Pydantic models for validation, matching schema in populate_db.py

class Customer(BaseModel):
    _id: str
    name: str
    country: str
    city: str
    state: str
    postal_code: Optional[float]

class Product(BaseModel):
    _id: str
    name: str
    price: float
    description: Optional[str] = None

class OrderItem(BaseModel):
    product_id: str  # References product _id in MongoDB
    quantity: int

class Order(BaseModel):
    _id: str
    customer_id: str  # References customer _id in MongoDB
    product_id: str   # References product _id in MongoDB
    quantity: int
    order_date: Optional[datetime] = None
    status: Optional[str] = "Completed"

# CRUD Endpoints for Customers
@app.post("/customers/")
def create_customer(customer: Customer):
    customer_data = customer.dict()
    
    # post customer into the database
    result = db.customers.insert_one(customer_data)
    
    # for retrieving customer with new generated customer ID
    new_customer = db.customers.find_one({"_id": result.inserted_id})
    
    if not new_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return to_dict(new_customer)  # Return dcreated customer details
@app.get("/customers/{customer_id}")
def read_customer(customer_id: str):
    customer = db.customers.find_one({"_id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return to_dict(customer)

@app.put("/customers/{customer_id}")
def update_customer(customer_id: str, customer: Customer):
    result = db.customers.update_one(
        {"_id": customer_id}, {"$set": customer.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer updated successfully"}

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: str):
    result = db.customers.delete_one({"_id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

# CRUD Endpoints for Products
@app.post("/products/")
def create_product(product: Product):
    product_data = product.dict()
    result = db.products.insert_one(product_data)
    return {"product_id": str(result.inserted_id)}

@app.get("/products/{product_id}")
def read_product(product_id: str):
    product = db.products.find_one({"_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return to_dict(product)

@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    result = db.products.update_one(
        {"_id": product_id}, {"$set": product.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    result = db.products.delete_one({"_id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# CRUD Endpoints for Orders

@app.post("/orders/")
def create_order(order: Order):
    # Verify customer exists
    if not db.customers.find_one({"_id": order.customer_id}):
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify product exists
    if not db.products.find_one({"_id": order.product_id}):
        raise HTTPException(status_code=404, detail="Product not found")

    order_data = order.dict()
    order_data["order_date"] = order_data.get("order_date", datetime.utcnow())
    result = db.orders.insert_one(order_data)
    return {"order_id": str(result.inserted_id)}

@app.get("/orders/{order_id}")
def read_order(order_id: str):
    order = db.orders.find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return to_dict(order)

@app.put("/orders/{order_id}")
def update_order(order_id: str, order: Order):
    # Verify customer exists
    if not db.customers.find_one({"_id": order.customer_id}):
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify product exists
    if not db.products.find_one({"_id": order.product_id}):
        raise HTTPException(status_code=404, detail="Product not found")

    order_data = order.dict(exclude_unset=True)
    result = db.orders.update_one({"_id": order_id}, {"$set": order_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order updated successfully"}

@app.delete("/orders/{order_id}")
def delete_order(order_id: str):
    result = db.orders.delete_one({"_id": order_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}


@app.get("/products/last")
def get_last_product():
    # Fetch the last product by sorting on the _id field in descending order (latest first)
    last_product_cursor = db.products.find().sort("_id", -1).limit(1)
    
    # Convert the cursor to a list to fetch the result
    last_product = list(last_product_cursor)
    
    # Check if the list is empty
    if not last_product:
        raise HTTPException(status_code=404, detail="No products found")
    
    # Return the last product as a dictionary (using to_dict to ensure _id is a string)
    return to_dict(last_product[0])
    
@app.get("/products/check_connection")
def check_connection():
    test_product = db.products.find_one()
    if not test_product:
        raise HTTPException(status_code=404, detail="No products found in the database")
    return {"message": "Connection successful", "sample_product": to_dict(test_product)}


