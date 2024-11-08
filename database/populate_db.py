import asyncio
from pymongo import MongoClient
import pandas as pd
from datetime import datetime

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["order_management"]

# Load dataset
df = pd.read_csv("database/train.csv")

async def populate_customers():
    # Filter out unique customers
    customers = df[['Customer ID', 'Customer Name', 'Country', 'City', 'State', 'Postal Code']].drop_duplicates(subset='Customer ID')
    customer_docs = [
        {
            "_id": row['Customer ID'],
            "name": row['Customer Name'],
            "country": row['Country'],
            "city": row['City'],
            "state": row['State'],
            "postal_code": row['Postal Code']
        }
        for _, row in customers.iterrows()
    ]

    # Insert customers with duplicate check
    for customer in customer_docs:
        # Insert only if the customer ID does not already exist
        if db.customers.count_documents({"_id": customer["_id"]}) == 0:
            db.customers.insert_one(customer)
        else:
            print(f"Customer with ID {customer['_id']} already exists, skipping insertion.")

    print("Customers populated.")

async def populate_products():
    # Filter out unique products
    products = df[['Product ID', 'Product Name', 'Category', 'Sales']].drop_duplicates(subset='Product ID')
    product_docs = [
        {
            "_id": row['Product ID'],
            "name": row['Product Name'],
            "description": row['Category'],
            "sales": row['Sales']
        }
        for _, row in products.iterrows()
    ]

    # Insert products with duplicate check
    for product in product_docs:
        if db.products.count_documents({"_id": product["_id"]}) == 0:
            db.products.insert_one(product)
        else:
            print(f"Product with ID {product['_id']} already exists, skipping insertion.")

    print("Products populated.")

async def populate_orders():
    # Remove duplicates based on 'Order ID'
    orders = df[['Order ID', 'Customer ID', 'Product ID', 'Order Date']].drop_duplicates(subset='Order ID')
    
    # Create the documents to insert into MongoDB
    order_docs = [
        {
            "_id": row['Order ID'],
            "customer_id": row['Customer ID'],
            "product_id": row['Product ID'],
            "quantity": 1,  # Default quantity since it is not available in the dataset
            "order_date": datetime.strptime(row['Order Date'], "%d/%m/%Y"),
            "status": "Completed"  # Default status
        }
        for _, row in orders.iterrows()
    ]

    # Insert orders with duplicate check
    for order in order_docs:
        if db.orders.count_documents({"_id": order["_id"]}) == 0:
            db.orders.insert_one(order)
        else:
            print(f"Order with ID {order['_id']} already exists, skipping insertion.")

    print("Orders populated.")

async def main():
    # Clear existing data in collections
    db.customers.delete_many({})
    db.products.delete_many({})
    db.orders.delete_many({})

    # Populate the collections
    await populate_customers()
    await populate_products()
    await populate_orders()

if __name__ == "__main__":
    asyncio.run(main())
