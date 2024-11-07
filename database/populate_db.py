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
    customers = df[['Customer ID', 'Customer Name']].drop_duplicates()
    customer_docs = [
        {
            "_id": row['Customer ID'],
            "name": row['Customer Name'],
            "email": f"{row['Customer Name'].replace(' ', '.')}@example.com",
            "address": "123 Default St"
        }
        for _, row in customers.iterrows()
    ]
    db.customers.insert_many(customer_docs)
    print("Customers populated.")

async def populate_products():
    products = df[['Product ID', 'Product Name', 'Sales']].drop_duplicates(subset='Product ID')
    product_docs = [
        {
            "_id": row['Product ID'],
            "name": row['Product Name'],
            "description": "No description",
            "price": row['Sales']
        }
        for _, row in products.iterrows()
    ]
    db.products.insert_many(product_docs)
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
    
    # Insert the documents into the 'orders' collection
    db.orders.insert_many(order_docs)
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
