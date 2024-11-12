import requests
import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def fetch_latest_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()  # Return the data in JSON format
    else:
        raise Exception(f"Error fetching data from API. Status code: {response.status_code}")

def load_model(model_path):
    # Load the pre-trained model from the provided path
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
    return model

def preprocess_data(data):
    # Example: Encoding categorical features using Label Encoding for simplicity
    label_encoder = LabelEncoder()

    # Encode categorical columns
    categorical_columns = ['Customer Name', 'City', 'State', 'Product Name', 'Category']
    
    # Make sure all categorical columns are present in the data
    for column in categorical_columns:
        if column in data.columns:
            data[column] = label_encoder.fit_transform(data[column].astype(str))
    
    # Ensure all necessary features are included, and handle missing data if needed
    feature_columns = ['Order ID', 'Customer ID', 'Customer Name', 'City', 'State', 
                       'Postal Code', 'Product ID', 'Category', 'Product Name', 'Order_day', 
                       'Order_month', 'Order_year']
    
    # Select the relevant features for prediction
    data = data[feature_columns].fillna(0)  # Handle any missing data (you can choose another strategy)
    
    return data

def make_prediction(model, data):
    # Make a prediction based on the input data
    prediction = model.predict(data)
    return prediction

# Example usage
api_url = "http://localhost:8000"  # Replace actual API URL
model_path = "model.pkl"  # Replace with your actual model path

# Fetch latest data
latest_data = fetch_latest_data(api_url)

# Load trained model
model = load_model(model_path)

# Convert the latest data to a DataFrame
data = pd.DataFrame([latest_data])  # Assuming the API returns data as a dictionary
processed_data = preprocess_data(data)

# Make prediction
prediction = make_prediction(model, processed_data)
print(f"Predicted Sales: {prediction[0]}")
