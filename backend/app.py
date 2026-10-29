# Import Flask for web server
from flask import Flask, request, jsonify
# Import CORS to allow frontend to communicate with backend
from flask_cors import CORS
# Import joblib to load saved ML models
import joblib
# Import pandas to work with customer data
import pandas as pd
# Import os to handle file paths
import os

# Create Flask application
app = Flask(__name__)
# Enable CORS so frontend (HTML/JS) can call this API
CORS(app)

# ============================================================
# STEP 1: Define file paths for ML models and data
# ============================================================

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Build paths to the model, scaler, and customer data
MODEL_PATH = os.path.join(BASE_DIR, "ml", "churn_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")
DATA_PATH = os.path.join(BASE_DIR, "ml", "telco_churn.csv")

# ============================================================
# STEP 2: Load the trained ML model and customer data
# ============================================================

# Load the pre-trained churn prediction model
model = joblib.load(MODEL_PATH)
# Load the scaler (used to normalize features)
scaler = joblib.load(SCALER_PATH)
# Load the customer database as a DataFrame
df_customers = pd.read_csv(DATA_PATH)

# Clean the TotalCharges column (convert text to numbers)
df_customers['TotalCharges'] = pd.to_numeric(df_customers['TotalCharges'], errors='coerce')
# Calculate median to fill any missing values later
TOTAL_CHARGES_MEDIAN = df_customers['TotalCharges'].median()

# ============================================================
# STEP 3: Define the exact 30 features used during training
# ============================================================
# These must match exactly what the model was trained on
# Order matters! Each position corresponds to a specific feature

FEATURE_NAMES = [
    "SeniorCitizen",                      # Is customer a senior citizen (0 or 1)
    "tenure",                             # How many months customer has been with company
    "MonthlyCharges",                     # Monthly bill amount
    "TotalCharges",                       # Total amount paid over tenure
    "gender_Male",                        # 1 if Male, 0 if Female
    "Partner_Yes",                        # 1 if has partner, 0 if no
    "Dependents_Yes",                     # 1 if has dependents, 0 if no
    "PhoneService_Yes",                   # 1 if has phone service
    "MultipleLines_No phone service",     # 1 if no phone service
    "MultipleLines_Yes",                  # 1 if has multiple phone lines
    "InternetService_Fiber optic",        # 1 if uses fiber optic internet
    "InternetService_No",                 # 1 if has no internet service
    "OnlineSecurity_No internet service", # 1 if no internet (so no online security)
    "OnlineSecurity_Yes",                 # 1 if has online security
    "OnlineBackup_No internet service",   # 1 if no internet (so no backup)
    "OnlineBackup_Yes",                   # 1 if has online backup
    "DeviceProtection_No internet service", # 1 if no internet (so no device protection)
    "DeviceProtection_Yes",               # 1 if has device protection
    "TechSupport_No internet service",    # 1 if no internet (so no tech support)
    "TechSupport_Yes",                    # 1 if has tech support
    "StreamingTV_No internet service",    # 1 if no internet (so no streaming TV)
    "StreamingTV_Yes",                    # 1 if has streaming TV
    "StreamingMovies_No internet service", # 1 if no internet (so no streaming movies)
    "StreamingMovies_Yes",                # 1 if has streaming movies
    "Contract_One year",                  # 1 if on 1-year contract
    "Contract_Two year",                  # 1 if on 2-year contract
    "PaperlessBilling_Yes",               # 1 if uses paperless billing
    "PaymentMethod_Credit card (automatic)", # 1 if pays by auto credit card
    "PaymentMethod_Electronic check",     # 1 if pays by electronic check
    "PaymentMethod_Mailed check"          # 1 if pays by mailed check
]

# ============================================================
# STEP 4: Create API endpoint for homepage
# ============================================================

@app.route("/")
def home():
    """
    Health check endpoint
    Returns a simple message to confirm API is running
    """
    return jsonify({
        "message": "Customer Retention Intelligence API is running!"
    })

# ============================================================
# STEP 5: Create prediction endpoint
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint
    Receives a customer ID and returns churn prediction
    """
    try:
        # Get JSON data sent from frontend
        data = request.get_json()
        
        # Check if customerID was provided
        if "customerID" not in data:
            return jsonify({"error": "customerID is required"}), 400
        
        customer_id = data["customerID"]
        
        # ============================================================
        # STEP 5.1: Find customer in the dataset
        # ============================================================
        customer_row = df_customers[df_customers["customerID"] == customer_id]
        
        # If customer not found, return error
        if customer_row.empty:
            return jsonify({"error": "Customer ID not found"}), 404
        
        # Get the first (and only) matching row
        customer_data = customer_row.iloc[0].copy()
        
        # ============================================================
        # STEP 5.2: Prepare features for ML prediction
        # ============================================================
        
        # Remove customerID (not used for prediction)
        customer_features = customer_data.drop(['customerID'])
        
        # Remove Churn column if it exists (this is what we're predicting)
        if 'Churn' in customer_features.index:
            customer_features = customer_features.drop(['Churn'])
        
        # Handle missing TotalCharges values
        if pd.isna(customer_features['TotalCharges']):
            customer_features['TotalCharges'] = TOTAL_CHARGES_MEDIAN
        else:
            customer_features['TotalCharges'] = float(customer_features['TotalCharges'])
        
        # ============================================================
        # STEP 5.3: Convert categorical features to numbers
        # ============================================================
        
        # Create a DataFrame with one row (for encoding)
        customer_df = pd.DataFrame([customer_features])
        
        # Apply one-hot encoding (same as training)
        # This converts text categories into binary columns (0 or 1)
        customer_encoded = pd.get_dummies(customer_df, drop_first=True, dtype=int)
        
        # ============================================================
        # STEP 5.4: Ensure we have exactly 30 features in correct order
        # ============================================================
        
        # Create a DataFrame with all 30 features, initialized to 0
        customer_final = pd.DataFrame(0, index=[0], columns=FEATURE_NAMES)
        
        # Fill in the features that exist for this customer
        for col in customer_encoded.columns:
            if col in FEATURE_NAMES:
                customer_final[col] = customer_encoded[col].values[0]
        
        # Ensure columns are in the exact order the model expects
        customer_final = customer_final[FEATURE_NAMES]
        
        # ============================================================
        # STEP 5.5: Scale the features
        # ============================================================
        # ML models work better when all numbers are on similar scale
        customer_scaled = scaler.transform(customer_final)
        
        # ============================================================
        # STEP 5.6: Make prediction
        # ============================================================
        
        # Predict: 0 = Stay, 1 = Churn
        prediction = model.predict(customer_scaled)[0]
        
        # Get probability (0.0 to 1.0) that customer will churn
        probability = model.predict_proba(customer_scaled)[0][1]
        
        # Convert prediction to readable text
        prediction_text = "CHURN" if prediction == 1 else "STAY"
        
        # ============================================================
        # STEP 5.7: Build response with all customer details
        # ============================================================
        
        response = {
            # Prediction results
            "customerID": customer_id,
            "prediction": prediction_text,
            "churn_probability": probability,
            
            # Customer demographic info
            "gender": customer_data.get("gender", ""),
            "SeniorCitizen": int(customer_data.get("SeniorCitizen", 0)),
            "Partner": customer_data.get("Partner", ""),
            "Dependents": customer_data.get("Dependents", ""),
            
            # Account info
            "tenure": int(customer_data.get("tenure", 0)),
            "Contract": customer_data.get("Contract", ""),
            "PaperlessBilling": customer_data.get("PaperlessBilling", ""),
            "PaymentMethod": customer_data.get("PaymentMethod", ""),
            "MonthlyCharges": float(customer_data.get("MonthlyCharges", 0)),
            "TotalCharges": float(customer_features["TotalCharges"]),
            
            # Services subscribed
            "PhoneService": customer_data.get("PhoneService", ""),
            "MultipleLines": customer_data.get("MultipleLines", ""),
            "InternetService": customer_data.get("InternetService", ""),
            "OnlineSecurity": customer_data.get("OnlineSecurity", ""),
            "OnlineBackup": customer_data.get("OnlineBackup", ""),
            "DeviceProtection": customer_data.get("DeviceProtection", ""),
            "TechSupport": customer_data.get("TechSupport", ""),
            "StreamingTV": customer_data.get("StreamingTV", ""),
            "StreamingMovies": customer_data.get("StreamingMovies", "")
        }
        
        # Return response as JSON
        return jsonify(response)
        
    except Exception as e:
        # If any error occurs, return error message
        return jsonify({"error": str(e)}), 400

# ============================================================
# STEP 6: Start the Flask server
# ============================================================

if __name__ == "__main__":
    # Run on localhost port 5000
    app.run(host="127.0.0.1", port=5000, debug=True)
