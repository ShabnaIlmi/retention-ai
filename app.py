import warnings
import numpy as np
import pickle
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, logging
import joblib

# Suppress Specific Sklearn Warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

app = Flask(__name__)

# Configure logging
import logging
app.logger.setLevel(logging.INFO)

# Load Pretrained Models - Removed Scalers
try:
    # First set of models - removing scalers
    with open('models/telecom_model.pkl', 'rb') as f:
        telecom_model = pickle.load(f)

    with open('models/banking_model.pkl', 'rb') as f:
        banking_model = pickle.load(f)
    
    # Loading alternative models if the first attempt fails
    # These can be used as fallbacks
    try:
        bank_model = joblib.load("banking_model.pkl")
        telecom_model_joblib = joblib.load("telecom_model.pkl")
    except Exception as e:
        app.logger.info(f"Joblib models not found, using pickle models: {e}")
        bank_model = banking_model
        telecom_model_joblib = telecom_model

except Exception as e:
    print(f"Error loading models: {e}")
    exit(1)

# Function to Parse Telecom Customer Form Data
def parse_telecom_form(form_data):
    try:
        # Extract form fields
        tenure = int(form_data['tenure'])
        monthly_charges = float(form_data['monthly_charges'])
        total_charges = float(form_data['total_charges'])
        paperless_billing = int(form_data['paperless_billing'])
        senior_citizen = int(form_data['senior_citizen'])
        streaming_tv = int(form_data['streaming_tv'])
        streaming_movies = int(form_data['streaming_movies'])
        multiple_lines = int(form_data['multiple_lines'])
        phone_service = int(form_data['phone_service'])
        device_protection = int(form_data['device_protection'])
        online_backup = int(form_data['online_backup'])
        partner = int(form_data['partner'])
        dependents = int(form_data['dependents'])
        tech_support = int(form_data['tech_support'])
        online_security = int(form_data['online_security'])
        gender = form_data['gender']
        contract = form_data['contract']
        internet_service = form_data['internet_service']
        payment_method = form_data['payment_method']

        # One-hot Encoding Categorical Variables
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

        # Create Features Array in the same format as in the code
        features = [paperless_billing, senior_citizen, streaming_tv, streaming_movies,
                    multiple_lines, phone_service, device_protection, online_backup,
                    partner, dependents, tech_support, online_security,
                    monthly_charges, total_charges, tenure] + \
                   contract_encoded + internet_service_encoded + payment_method_encoded + gender_encoded
                    
        return np.array(features).reshape(1, -1)

    except KeyError as e:
        raise ValueError(f"Missing required field: {e}")
    except Exception as e:
        raise ValueError(f"Error processing form data: {e}")

# Function to Parse Bank Customer Form Data
def parse_banking_form(form_data):
    try:
        # Extract form fields
        credit_score = int(form_data['credit_score'])
        age = int(form_data['age'])
        tenure = int(form_data['tenure'])
        balance = float(form_data['balance'])
        num_of_products = int(form_data['num_of_products'])
        has_cr_card = int(form_data['has_cr_card'])
        is_active_member = int(form_data['is_active_member'])
        estimated_salary = float(form_data['estimated_salary'])
        satisfaction_score = int(form_data['satisfaction_score'])
        point_earned = int(form_data['point_earned'])
        gender = form_data['gender']
        card_type = form_data['card_type']

        # One-hot Encoding Categorical Variables
        gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]
        card_type_encoded = [1 if card_type == "DIAMOND" else 0,
                             1 if card_type == "GOLD" else 0,
                             1 if card_type == "SILVER" else 0,
                             1 if card_type == "PLATINUM" else 0]

        # Create Feature Array in the same format as in the code
        features = [credit_score, age, tenure, balance, num_of_products,
                    has_cr_card, is_active_member, estimated_salary,
                    satisfaction_score, point_earned] + \
                   gender_encoded + card_type_encoded
                    
        return np.array(features).reshape(1, -1)

    except KeyError as e:
        raise ValueError(f"Missing required field: {e}")
    except Exception as e:
        raise ValueError(f"Error processing form data: {e}")

# Function to predict churn
def predict_churn(model, features):
    # Check if features is already a 2D array or needs reshaping
    if len(np.array(features).shape) == 1:
        # If it's a 1D array (flat list), reshape it
        features = np.array(features).reshape(1, -1)
    
    # Direct prediction without scaling
    prediction = model.predict(features)
    return "Churned" if prediction[0] == 1 else "Not Churned"

# API Routes for JSON requests
# Predict Bank Churn
@app.route('/api/bank-churn-prediction', methods=['POST'])
def predict_banking_api():
    try:
        # Log incoming data for debugging
        form_data = request.get_json()
        app.logger.info(f"Received banking data: {form_data}")
        app.logger.info(f"Processing banking form data: {form_data}")
        
        # Parse the form data
        user_data = parse_banking_form(form_data)
        app.logger.info(f"Banking features shape: {user_data.shape}")
        
        # Direct prediction without scaling
        prediction = banking_model.predict(user_data)
        app.logger.info(f"Prediction result: {prediction}")
        
        # Return the prediction result
        return jsonify({'prediction': "Churned" if prediction[0] == 1 else "Not Churned"})
    except ValueError as e:
        app.logger.error(f"ValueError in banking prediction: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Exception in banking prediction: {str(e)}")
        return jsonify({'error': 'An error occurred during prediction.'}), 500

# Predict Telecom Churn
@app.route('/api/telecom-churn-prediction', methods=['POST'])
def predict_telecom_api():
    try:
        # Log incoming data for debugging
        form_data = request.get_json()
        app.logger.info(f"Received telecom data: {form_data}")
        app.logger.info(f"Processing telecom form data: {form_data}")
        
        # Parse the form data
        user_data = parse_telecom_form(form_data)
        app.logger.info(f"Telecom features shape: {user_data.shape}")
        
        # Direct prediction without scaling
        prediction = telecom_model.predict(user_data)
        app.logger.info(f"Prediction result: {prediction}")
        
        # Return the prediction result
        return jsonify({'prediction': "Churned" if prediction[0] == 1 else "Not Churned"})
    except ValueError as e:
        app.logger.error(f"ValueError in telecom prediction: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Exception in telecom prediction: {str(e)}")
        return jsonify({'error': 'An error occurred during prediction.'}), 500

# Web Routes for Form submissions
# Home page route
@app.route('/')
@app.route('/index.html')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Error loading Home page: {str(e)}")
        return f"Error loading Home page: {str(e)}", 500

# About Me page route
@app.route('/aboutme')
@app.route('/AboutMe.html')
def aboutme():
    try:
        return render_template('AboutMe.html')
    except Exception as e:
        app.logger.error(f"Error loading AboutMe page: {str(e)}")
        return f"Error loading AboutMe page: {str(e)}", 500

# Bank customer prediction route
@app.route('/predict-bank', methods=['POST'])
def predict_bank():
    try:
        if request.method == 'POST':
            # Collecting input from the form
            credit_score = int(request.form['credit_score'])
            gender = request.form['gender']
            age = int(request.form['age'])
            tenure = int(request.form['tenure'])
            balance = float(request.form['balance'])
            num_of_products = int(request.form['num_of_products'])
            has_cr_card = int(request.form['has_cr_card'])
            is_active_member = int(request.form['is_active_member'])
            estimated_salary = float(request.form['estimated_salary'])
            satisfaction_score = int(request.form['satisfaction_score'])
            card_type = request.form['card_type']
            points_earned = int(request.form['points_earned'])

            # Log the received data
            app.logger.info(f"Bank form data: credit_score={credit_score}, gender={gender}, age={age}, tenure={tenure}")

            # One-hot Encoding
            gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]
            card_type_encoded = [1 if card_type == "DIAMOND" else 0, 
                                1 if card_type == "GOLD" else 0, 
                                1 if card_type == "SILVER" else 0, 
                                1 if card_type == "PLATINUM" else 0]

            # Create feature array in consistent style
            features = [credit_score, age, tenure, balance, num_of_products, 
                       has_cr_card, is_active_member, estimated_salary, 
                       satisfaction_score, points_earned] + \
                      gender_encoded + card_type_encoded

            # Predict churn directly without scaling
            result = predict_churn(bank_model, features)
            app.logger.info(f"Bank prediction result: {result}")

            # Render prediction result
            return render_template('index.html', prediction_result=f"Predicted Churn Status: {result}")

    except Exception as e:
        app.logger.error(f"Error during prediction for bank: {str(e)}")
        return f"Error during prediction: {str(e)}", 500

# Telecom customer prediction route
@app.route('/predict-telecom', methods=['POST'])
def predict_telecom():
    try:
        if request.method == 'POST':
            # Collecting input from the form
            tenure = int(request.form['tenure'])
            monthly_charges = float(request.form['monthly_charges'])
            total_charges = float(request.form['total_charges'])
            contract = request.form['contract']
            internet_service = request.form['internet_service']
            payment_method = request.form['payment_method']
            paperless_billing = int(request.form['paperless_billing'])
            senior_citizen = int(request.form['senior_citizen'])
            streaming_tv = int(request.form['streaming_tv'])
            streaming_movies = int(request.form['streaming_movies'])
            multiple_lines = int(request.form['multiple_lines'])
            phone_service = int(request.form['phone_service'])
            device_protection = int(request.form['device_protection'])
            online_backup = int(request.form['online_backup'])
            partner = int(request.form['partner'])
            dependents = int(request.form['dependents'])
            tech_support = int(request.form['tech_support'])
            online_security = int(request.form['online_security'])
            gender = request.form['gender']

            # Log the received data
            app.logger.info(f"Telecom form data: tenure={tenure}, monthly_charges={monthly_charges}, contract={contract}")

            # One-hot Encoding
            gender_encoded = [1 if gender == "Male" else 0, 1 if gender == "Female" else 0]
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

            # Create features array
            features = [paperless_billing, senior_citizen, streaming_tv, streaming_movies,
                        multiple_lines, phone_service, device_protection, online_backup,
                        partner, dependents, tech_support, online_security,
                        monthly_charges, total_charges, tenure] + \
                       contract_encoded + internet_service_encoded + payment_method_encoded + gender_encoded

            # Predict churn directly without scaling
            result = predict_churn(telecom_model_joblib, features)
            app.logger.info(f"Telecom prediction result: {result}")

            # Render prediction result
            return render_template('index.html', prediction_result=f"Predicted Churn Status: {result}")
    except Exception as e:
        app.logger.error(f"Error during prediction for telecom: {str(e)}")
        return f"Error during prediction: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)