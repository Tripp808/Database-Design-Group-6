import pandas as pd
from pymongo import MongoClient

# Load the dataset
file_path = './train.csv'
dataset = pd.read_csv(file_path)

# Connect to MongoDB
client = MongoClient("mongodb+srv://aibeh:Parity2017@cluster0.nekvn.mongodb.net/?")
db = client['sales_database']

# Create collections
customers_collection = db['Customers']
products_collection = db['Products']
orders_collection = db['Orders']
sales_collection = db['Sales']

# Insert data into collections with appropriate nesting and references
for _, row in dataset.iterrows():
    # Insert customer data if not already present
    customer_data = {
        "_id": row['Customer ID'],
        "name": row['Customer Name'],
        "segment": row['Segment'],
        "location": {
            "country": row['Country'],
            "city": row['City'],
            "state": row['State'],
            "postal_code": row['Postal Code'],
            "region": row['Region']
        }
    }
    customers_collection.update_one(
        {"_id": row['Customer ID']},
        {"$setOnInsert": customer_data},
        upsert=True
    )

# Insert product data if not already present
    product_data = {
        "_id": row['Product ID'],
        "category": row['Category'],
        "sub_category": row['Sub-Category'],
        "product_name": row['Product Name']
    }
    products_collection.update_one(
        {"_id": row['Product ID']},
        {"$setOnInsert": product_data},
        upsert=True
    )

     