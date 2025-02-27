import streamlit as st
import numpy as np
import joblib

# Load models and scalers
bank_model = joblib.load("models/banking_model.pkl")
telecom_model = joblib.load("models/telecom_model.pkl")
bank_scaler = joblib.load("models/banking_scaler.pkl")
telecom_scaler = joblib.load("models/telecom_scaler.pkl")


# Function to predict churn
def predict_churn(model, scaler, features):
    scaled_features = scaler.transform([features])
    prediction = model.predict(scaled_features)
    return "Churned" if prediction[0] == 1 else "Not Churned"

# Streamlit UI
st.title("Churn Prediction App")

# Model Selection
model_type = st.radio("Choose the type of Churn Prediction:", ["Bank Customer", "Telecom Customer"])

if model_type == "Bank Customer":
    st.header("Bank Customer Churn Prediction")

    # Input fields with validation
    credit_score = st.number_input("Credit Score", min_value=300, max_value=900, step=1)
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", min_value=18, max_value=100)
    tenure = st.number_input("Tenure (Years)", min_value=0, max_value=10)
    balance = st.number_input("Balance")
    num_of_products = st.number_input("Number of Products", min_value=1, max_value=4)
    has_cr_card = st.radio("Has Credit Card?", [0, 1])
    is_active_member = st.radio("Is Active Member?", [0, 1])
    estimated_salary = st.number_input("Estimated Salary")
    satisfaction_score = st.slider("Satisfaction Score", 1, 5)
    card_type = st.selectbox("Card Type", ["DIAMOND", "GOLD", "SILVER", "PLATINUM"])
    points_earned = st.number_input("Points Earned", min_value=0)

    # Check for empty inputs
    if st.button("Predict"):
        if (credit_score == 0 or age == 0 or tenure == 0 or balance == 0 or 
            num_of_products == 0 or estimated_salary == 0 or satisfaction_score == 0 or points_earned == 0):
            st.error("Please fill in all the fields correctly before submitting.")
        else:
            # One-hot Encoding
            gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]
            card_type_encoded = [1 if card_type == "DIAMOND" else 0, 1 if card_type == "GOLD" else 0, 
                                 1 if card_type == "SILVER" else 0, 1 if card_type == "PLATINUM" else 0]

            # Create Feature Array
            features = np.array([credit_score, age, tenure, balance, num_of_products,
                                 has_cr_card, is_active_member, estimated_salary,
                                 satisfaction_score, points_earned] +gender_encoded + card_type_encoded)

            result = predict_churn(bank_model, bank_scaler, features)
            st.success(f"Predicted Churn Status: {result}")

elif model_type == "Telecom Customer":
    st.header("Telecom Customer Churn Prediction")

    # Input fields with validation
    tenure = st.number_input("Tenure", min_value=0, max_value=100)
    monthly_charges = st.number_input("Monthly Charges")
    total_charges = st.number_input("Total Charges")
    contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
    internet_service = st.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])
    payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
    paperless_billing = st.radio("Paperless Billing?", [0, 1])
    senior_citizen = st.radio("Senior Citizen?", [0, 1])
    streaming_tv = st.radio("Streaming TV?", [0, 1])
    streaming_movies = st.radio("Streaming Movies?", [0, 1])
    multiple_lines = st.radio("Multiple Lines?", [0, 1])
    phone_service = st.radio("Phone Service?", [0, 1])
    device_protection = st.radio("Device Protection?", [0, 1])
    online_backup = st.radio("Online Backup?", [0, 1])
    partner = st.radio("Partner?", [0, 1])
    dependents = st.radio("Dependents?", [0, 1])
    tech_support = st.radio("Tech Support?", [0, 1])
    online_security = st.radio("Online Security?", [0, 1])
    gender = st.selectbox("Gender", ["Male", "Female"])

    # Check for empty inputs
    if st.button("Predict"):
        if (monthly_charges == 0 or total_charges == 0 or tenure == 0):
            st.error("Please fill in all the fields correctly before submitting.")
        else:
            # One-hot Encoding
            contract_encoded = [1 if contract == "Month-to-month" else 0, 1 if contract == "One year" else 0, 1 if contract == "Two year" else 0]
            internet_service_encoded = [1 if internet_service == "Fiber optic" else 0, 
                                        1 if internet_service == "DSL" else 0, 1 if internet_service == "No" else 0]
            payment_method_encoded = [1 if payment_method == "Electronic check" else 0, 
                                      1 if payment_method == "Mailed check" else 0, 1 if payment_method == "Bank transfer (automatic)" else 0, 
                                      1 if payment_method == "Credit card (automatic)" else 0]
            gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]

            # Feature Array
            features = np.array([paperless_billing, senior_citizen, streaming_tv, streaming_movies,
                                 multiple_lines, phone_service, device_protection, online_backup,
                                 partner, dependents, tech_support, online_security,
                                 monthly_charges, total_charges, tenure] + contract_encoded + internet_service_encoded + payment_method_encoded + gender_encoded)

            result = predict_churn(telecom_model, telecom_scaler, features)
            st.success(f"Predicted Churn Status: {result}")
