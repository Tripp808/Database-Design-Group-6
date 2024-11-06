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

