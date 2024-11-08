import requests
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import pickle  

# BASE URL FastAPI 
BASE_URL = "http://127.0.0.1:8000"

# Define the features to match the trained model
features = ["Country", "State", "Postal Code", "Category"]

# Fetch data from each endpoint and structure it as required
def fetch_latest_order_data():
    # Fetch the latest order
    response = requests.get(f"{BASE_URL}/orders/")
    if response.status_code == 200:
        orders = response.json()
        if orders:
            latest_order = orders[-1]
            order_data = latest_order["items"]
            customer_id = latest_order["customer_id"]

            # Fetch customer information
            customer_response = requests.get(f"{BASE_URL}/customers/{customer_id}")
            if customer_response.status_code == 200:
                customer_info = customer_response.json()
                latest_order.update(customer_info)

            # Fetch product information for each item in the order
            for item in order_data:
                product_response = requests.get(f"{BASE_URL}/products/{item['product_id']}")
                if product_response.status_code == 200:
                    product_info = product_response.json()
                    item.update(product_info)

            # Flatten order data into a single dictionary
            latest_entry = {
                "Country": customer_info.get("country", ""),
                "State": customer_info.get("state", ""),
                "Postal Code": customer_info.get("postal_code", ""),
                "Category": order_data[0].get("category", "")  # Assuming first item's category for simplicity
            }
            return pd.DataFrame([latest_entry])
    return None

# Load the pre-trained model
def load_model():
    with open("prediction/trained_model.pkl", "rb") as file:
        model = pickle.load(file)
    return model

# Prepare data and make prediction
def predict_latest_order():
    model = load_model()
    latest_order_data = fetch_latest_order_data()
    
    if latest_order_data is not None:
        # Drop rows with missing values in the required columns
        latest_order_data = latest_order_data.dropna(subset=features)

        # Encode categorical features consistently
        for column in latest_order_data.select_dtypes(include=['object']).columns:
            latest_order_data[column] = LabelEncoder().fit_transform(latest_order_data[column])

        # Make prediction
        prediction = model.predict(latest_order_data[features])
        print("Predicted Sales Value for the latest order:", prediction[0])
    else:
        print("Failed to fetch latest order data.")

# Main execution
if __name__ == "__main__":
    predict_latest_order()
