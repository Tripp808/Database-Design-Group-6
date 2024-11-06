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
# Insert order data if not already present
    order_data = {
        "_id": row['Order ID'],
        "order_date": row['Order Date'],
        "ship_date": row['Ship Date'],
        "ship_mode": row['Ship Mode'],
        "customer_id": row['Customer ID']
    }
    orders_collection.update_one(
        {"_id": row['Order ID']},
        {"$setOnInsert": order_data},
        upsert=True
    )

# Insert sales data
    sales_data = {
        "order_id": row['Order ID'],
        "product_id": row['Product ID'],
        "sales_amount": row['Sales']
    }
    sales_collection.insert_one(sales_data)

print("Data inserted successfully!")

     