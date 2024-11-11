import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import pickle

# Load your dataset
data = pd.read_csv('database/train.csv')  

# Define features and target
features = ["Country", "State", "Postal Code", "Category"]
target = "Sales"  # Replace with your actual target column

# Initialize label encoders dictionary
label_encoders = {}

# Preprocess the data
for column in data.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    data[column] = le.fit_transform(data[column])
    label_encoders[column] = le  # Save the encoder for this column

# Drop rows with missing values
data = data.dropna(subset=features + [target])

# Separate features and target
X = data[features]
y = data[target]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the trained model and encoders
with open("prediction/trained_model.pkl", "wb") as file:
    pickle.dump(model, file)

with open("prediction/label_encoders.pkl", "wb") as file:
    pickle.dump(label_encoders, file)
