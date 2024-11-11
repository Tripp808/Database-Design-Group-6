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
    
    return to_dict(new_customer)  # Return created customer details

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
    # customer verification
    if not db.customers.find_one({"_id": order.customer_id}):
        raise HTTPException(status_code=404, detail="Customer not found")

    # product exists?
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

# Get the last product
@app.get("/products/last")
def get_last_product():
    last_product_cursor = db.products.find().sort("_id", -1).limit(1)
    last_product = list(last_product_cursor)
    
    if not last_product:
        raise HTTPException(status_code=404, detail="No products found")
    
    return to_dict(last_product[0])

# Get the last order
@app.get("/orders/last")
def get_last_order():
    # Try to fetch the last order (adjust based on your schema)
    last_order_cursor = db.orders.find().sort("_id", -1).limit(1)
    
    # Convert the cursor to a list to fetch the result
    last_order = list(last_order_cursor)
    
    # Check if the result is empty
    if not last_order:
        raise HTTPException(status_code=404, detail="No orders found")
    
    # Convert the last order to a dictionary using the helper
    last_order_dict = to_dict(last_order[0])

    # Fetch customer details using customer_id from the order
    customer = db.customers.find_one({"_id": last_order_dict["customer_id"]})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Fetch product details using product_id from the order
    product = db.products.find_one({"_id": last_order_dict["product_id"]})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Select only the relevant fields for prediction
    prediction_data = {
        "Order ID": last_order_dict["_id"],
        "Customer ID": last_order_dict["customer_id"],
        "Customer Name": customer["name"],  # Fetch customer name from the customers collection
        "City": customer["city"],  # Fetch city from the customer data
        "State": customer["state"],  # Fetch state from the customer data
        "Postal Code": customer.get("postal_code", None),  # Fetch postal code, if exists
        "Product ID": last_order_dict["product_id"],
        "Category": product.get("category", None),  # Fetch category from product
        "Product Name": product["name"],  # Fetch product name from the product collection
        "Order_day": last_order_dict["order_date"].day,
        "Order_month": last_order_dict["order_date"].month,
        "Order_year": last_order_dict["order_date"].year
    }

    return prediction_data
