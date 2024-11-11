import requests
import pandas as pd
import pickle

BASE_URL = "http://127.0.0.1:8000"  # FastAPI base URL

# Features required by the model (ensure these match with training data)
features = ["Country", "State", "Postal Code", "Category"]

# Fetch the latest order data from the API
def fetch_latest_order_data():
    # Fetch the latest order
    response = requests.get(f"{BASE_URL}/orders/latest")
    if response.status_code == 200:
        latest_order = response.json()
        customer_id = latest_order["customer_id"]

        # Fetch customer information
        customer_response = requests.get(f"{BASE_URL}/customers/{customer_id}")
        if customer_response.status_code == 200:
            customer_info = customer_response.json()
            latest_entry = {
                "Country": customer_info.get("country", ""),
                "State": customer_info.get("state", ""),
                "Postal Code": customer_info.get("postal_code", 0)
            }

            # Fetch product information for the first item (assuming one item per order for simplicity)
            if latest_order["items"]:
                product_id = latest_order["items"][0].get("product_id")
                if product_id:
                    product_response = requests.get(f"{BASE_URL}/products/{product_id}")
                    if product_response.status_code == 200:
                        product_info = product_response.json()
                        latest_entry["Category"] = product_info.get("name", "Unknown")
                    else:
                        latest_entry["Category"] = "Unknown"
                else:
                    latest_entry["Category"] = "Unknown"
            else:
                latest_entry["Category"] = "Unknown"

            return pd.DataFrame([latest_entry])
    print("Failed to fetch data.")
    return None

# Load the trained model
def load_model():
    with open("prediction/trained_model.pkl", "rb") as file:
        model = pickle.load(file)
    return model

# Load the label encoders
def load_label_encoders():
    with open("prediction/label_encoders.pkl", "rb") as file:
        label_encoders = pickle.load(file)
    return label_encoders

# Prepare data and make prediction
def predict_latest_order():
    model = load_model()
    label_encoders = load_label_encoders()
    latest_order_data = fetch_latest_order_data()

    if latest_order_data is not None:
        # Ensure proper data formatting: Convert Postal Code to float
        latest_order_data["Postal Code"] = latest_order_data["Postal Code"].astype(float)

        # Apply label encoders to categorical fields
        for column in ["Country", "State", "Category"]:
            if column in label_encoders:
                latest_order_data[column] = label_encoders[column].transform(latest_order_data[column])

        # Make the prediction
        prediction = model.predict(latest_order_data[features])
        print("Predicted Sales Value for the latest order:", prediction[0])
    else:
        print("No data to predict.")

# Main execution
if __name__ == "__main__":
    predict_latest_order()
