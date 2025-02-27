import warnings
import numpy as np
import pickle
import os
import traceback
import streamlit as st

# Suppress Warnings
warnings.filterwarnings("ignore")

# Load Models & Scalers
def load_model(path):
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading {path}: {e}")
        return None

# Load models and scalers
telecom_model = load_model('models/telecom_model.pkl')
banking_model = load_model('models/banking_model.pkl')
telecom_scaler = load_model('models/telecom_scaler.pkl')
banking_scaler = load_model('models/banking_scaler.pkl')

# Streamlit App Title
st.title("Customer Churn Prediction")

# Sidebar Navigation
st.sidebar.header("Choose Prediction Type")
option = st.sidebar.radio("Select", ("Telecom Churn", "Banking Churn"))

# Function to Parse Telecom Data
def parse_telecom_data():
    st.sidebar.subheader("Telecom Customer Details")
    
    tenure = st.sidebar.number_input("Tenure (months)", min_value=0, max_value=100, step=1)
    monthly_charges = st.sidebar.number_input("Monthly Charges ($)", min_value=0.0, max_value=500.0)
    total_charges = st.sidebar.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0)
    paperless_billing = st.sidebar.radio("Paperless Billing", [0, 1])
    senior_citizen = st.sidebar.radio("Senior Citizen", [0, 1])
    streaming_tv = st.sidebar.radio("Streaming TV", [0, 1])
    streaming_movies = st.sidebar.radio("Streaming Movies", [0, 1])
    multiple_lines = st.sidebar.radio("Multiple Lines", [0, 1])
    phone_service = st.sidebar.radio("Phone Service", [0, 1])
    device_protection = st.sidebar.radio("Device Protection", [0, 1])
    online_backup = st.sidebar.radio("Online Backup", [0, 1])
    partner = st.sidebar.radio("Partner", [0, 1])
    dependents = st.sidebar.radio("Dependents", [0, 1])
    tech_support = st.sidebar.radio("Tech Support", [0, 1])
    online_security = st.sidebar.radio("Online Security", [0, 1])
    
    contract = st.sidebar.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    internet_service = st.sidebar.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])
    payment_method = st.sidebar.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
    gender = st.sidebar.selectbox("Gender", ["Male", "Female"])

    # One-hot encoding
    contract_encoded = [1 if contract == "Month-to-month" else 0, 1 if contract == "One year" else 0, 1 if contract == "Two year" else 0]
    internet_service_encoded = [1 if internet_service == "Fiber optic" else 0, 1 if internet_service == "DSL" else 0, 1 if internet_service == "No" else 0]
    payment_method_encoded = [1 if payment_method == "Electronic check" else 0, 1 if payment_method == "Mailed check" else 0, 1 if payment_method == "Bank transfer (automatic)" else 0, 1 if payment_method == "Credit card (automatic)" else 0]
    gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]

    # Feature Array
    features = np.array([paperless_billing, senior_citizen, streaming_tv, streaming_movies,
                         multiple_lines, phone_service, device_protection, online_backup,
                         partner, dependents, tech_support, online_security,
                         monthly_charges, total_charges, tenure] +
                        contract_encoded + internet_service_encoded + payment_method_encoded + gender_encoded).reshape(1, -1)
    
    return features

# Function to Parse Banking Data
def parse_banking_data():
    st.sidebar.subheader("Banking Customer Details")
    
    credit_score = st.sidebar.number_input("Credit Score", min_value=300, max_value=850, step=1)
    age = st.sidebar.number_input("Age", min_value=18, max_value=100, step=1)
    tenure = st.sidebar.number_input("Tenure (Years)", min_value=0, max_value=50, step=1)
    balance = st.sidebar.number_input("Account Balance ($)", min_value=0.0, max_value=1000000.0)
    num_of_products = st.sidebar.number_input("Number of Products", min_value=1, max_value=4, step=1)
    has_cr_card = st.sidebar.radio("Has Credit Card", [0, 1])
    is_active_member = st.sidebar.radio("Active Member", [0, 1])
    estimated_salary = st.sidebar.number_input("Estimated Salary ($)", min_value=0.0, max_value=500000.0)
    satisfaction_score = st.sidebar.number_input("Satisfaction Score", min_value=1, max_value=5, step=1)
    point_earned = st.sidebar.number_input("Loyalty Points Earned", min_value=0, max_value=1000, step=1)
    
    gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
    card_type = st.sidebar.selectbox("Card Type", ["DIAMOND", "GOLD", "SILVER", "PLATINUM"])

    # One-hot encoding
    gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]
    card_type_encoded = [1 if card_type == "DIAMOND" else 0, 1 if card_type == "GOLD" else 0, 1 if card_type == "SILVER" else 0, 1 if card_type == "PLATINUM" else 0]

    # Feature Array
    features = np.array([credit_score, age, tenure, balance, num_of_products,
                         has_cr_card, is_active_member, estimated_salary,
                         satisfaction_score, point_earned] +
                        gender_encoded + card_type_encoded).reshape(1, -1)
    
    return features

# Prediction Logic
if option == "Telecom Churn":
    user_data = parse_telecom_data()
    if st.sidebar.button("Predict Telecom Churn"):
        if telecom_model and telecom_scaler:
            user_data_scaled = telecom_scaler.transform(user_data)
            prediction = telecom_model.predict(user_data_scaled)
            result = "Churned" if prediction[0] == 1 else "Not Churned"
            st.success(f"Prediction: **{result}**")
        else:
            st.error("Telecom model is not loaded.")

elif option == "Banking Churn":
    user_data = parse_banking_data()
    if st.sidebar.button("Predict Banking Churn"):
        if banking_model and banking_scaler:
            user_data_scaled = banking_scaler.transform(user_data)
            prediction = banking_model.predict(user_data_scaled)
            result = "Churned" if prediction[0] == 1 else "Not Churned"
            st.success(f"Prediction: **{result}**")
        else:
            st.error("Banking model is not loaded.")
