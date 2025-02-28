from flask import Flask, request, jsonify, render_template
import numpy as np
import pickle
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

app = Flask(__name__)

# Load models and scalers
with open("banking_model.pkl", "rb") as f:
    bank_model = pickle.load(f)
with open("banking_scaler.pkl", "rb") as f:
    bank_scaler = pickle.load(f)

with open("telecom_model.pkl", "rb") as f:
    telecom_model = pickle.load(f)
with open("telecom_scaler.pkl", "rb") as f:
    telecom_scaler = pickle.load(f)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    model_type = data.get("model_type")  # Specify "bank" or "telecom"

    if model_type == "bank":
        feature_names = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts',
                         'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 'Complain',
                         'SatisfactionScore', 'PointsEarned', 'France', 'Germany', 'Spain',
                         'Male', 'Female', 'DIAMOND', 'GOLD', 'SILVER', 'PLATINUM']

        # Extracting values from request
        credit_score = int(data['CreditScore'])
        geography = data['Geography']
        gender = data['Gender']
        age = int(data['Age'])
        tenure = int(data['Tenure'])
        balance = float(data['Balance'])
        num_of_products = int(data['NumOfProducts'])
        has_cr_card = int(data['HasCrCard'])
        is_active_member = int(data['IsActiveMember'])
        estimated_salary = float(data['EstimatedSalary'])
        satisfaction_score = int(data['SatisfactionScore'])
        card_type = data['CardType']
        points_earned = int(data['PointsEarned'])

        # One-hot encoding
        geography_encoded = [1 if geography == "France" else 0,
                             1 if geography == "Germany" else 0,
                             1 if geography == "Spain" else 0]
        gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]
        card_type_encoded = [1 if card_type == "DIAMOND" else 0,
                             1 if card_type == "GOLD" else 0,
                             1 if card_type == "SILVER" else 0,
                             1 if card_type == "PLATINUM" else 0]

        # Create feature array
        features = np.array([credit_score, age, tenure, balance, num_of_products,
                             has_cr_card, is_active_member, estimated_salary,
                             satisfaction_score, points_earned] +
                            geography_encoded + gender_encoded + card_type_encoded).reshape(1, -1)
        features_scaled = bank_scaler.transform(features)
        prediction = bank_model.predict(features_scaled)

    elif model_type == "telecom":
        feature_names = ['Contract_Month-to-month', 'Contract_One year', 'Contract_Two year',
                         'InternetService_Fiber optic', 'InternetService_DSL', 'InternetService_No',
                         'PaymentMethod_Electronic check', 'PaymentMethod_Mailed check',
                         'PaymentMethod_Bank transfer (automatic)', 'PaymentMethod_Credit card (automatic)',
                         'PaperlessBilling', 'SeniorCitizen', 'StreamingTV', 'StreamingMovies',
                         'MultipleLines', 'PhoneService', 'gender_Male', 'gender_Female',
                         'DeviceProtection', 'OnlineBackup', 'Partner', 'Dependents', 'TechSupport',
                         'OnlineSecurity', 'MonthlyCharges', 'TotalCharges', 'tenure']

        # Extracting values from request
        tenure = int(data['Tenure'])
        monthly_charges = float(data['MonthlyCharges'])
        total_charges = float(data['TotalCharges'])
        contract = data['Contract']
        internet_service = data['InternetService']
        payment_method = data['PaymentMethod']
        paperless_billing = int(data['PaperlessBilling'])
        senior_citizen = int(data['SeniorCitizen'])
        streaming_tv = int(data['StreamingTV'])
        streaming_movies = int(data['StreamingMovies'])
        multiple_lines = int(data['MultipleLines'])
        phone_service = int(data['PhoneService'])
        device_protection = int(data['DeviceProtection'])
        online_backup = int(data['OnlineBackup'])
        partner = int(data['Partner'])
        dependents = int(data['Dependents'])
        tech_support = int(data['TechSupport'])
        online_security = int(data['OnlineSecurity'])
        gender = data['Gender']

        # One-hot encoding
        contract_encoded = [1 if contract == "Month-to-month" else 0,
                            1 if contract == "One year" else 0,
                            1 if contract == "Two year" else 0]
        internet_service_encoded = [1 if internet_service == "Fiber optic" else 0,
                                    1 if internet_service == "DSL" else 0,
                                    1 if internet_service == "No" else 0]
        payment_method_encoded = [1 if payment_method == "Electronic check" else 0,
                                  1 if payment_method == "Mailed check" else 0,
                                  1 if payment_method == "Bank transfer (automatic)" else 0,
                                  1 if payment_method == "Credit card (automatic)" else 0]
        gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]

        # Create feature array
        features = np.array([paperless_billing, senior_citizen, streaming_tv, streaming_movies,
                             multiple_lines, phone_service, device_protection, online_backup,
                             partner, dependents, tech_support, online_security,
                             monthly_charges, total_charges, tenure] +
                            contract_encoded + internet_service_encoded + payment_method_encoded + gender_encoded).reshape(1, -1)
        features_scaled = telecom_scaler.transform(features)
        prediction = telecom_model.predict(features_scaled)

    else:
        return jsonify({"error": "Invalid model type"})

    result = "Churned" if prediction[0] == 1 else "Not Churned"
    return jsonify({"prediction": result})

if __name__ == '__main__':
    # Get port from environment variable (Heroku sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    # Run the app, binding to all network interfaces (0.0.0.0)
    app.run(host='0.0.0.0', port=port)