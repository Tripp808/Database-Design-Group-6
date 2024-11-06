import pandas as pd
from pymongo import MongoClient

# Load the dataset
file_path = './train.csv'
dataset = pd.read_csv(file_path)

