# 🔧 BACKEND CODE EXPLANATION (app.py)

## Line-by-Line Breakdown

---

### **SECTION 1: Import Required Libraries**

```python
from flask import Flask, request, jsonify
```
- **Flask**: The web framework to create the API server
- **request**: To receive data sent from the frontend
- **jsonify**: To convert Python dictionaries to JSON format for sending to frontend

```python
from flask_cors import CORS
```
- **CORS**: Cross-Origin Resource Sharing - allows frontend (HTML file) running on different port/domain to communicate with this backend API

```python
import joblib
```
- **joblib**: Used to load the pre-trained machine learning model and scaler from .pkl files

```python
import pandas as pd
```
- **pandas**: Powerful library for working with data in tables (DataFrames)
- Used here to load and search customer data from CSV file

```python
import os
```
- **os**: Operating system module to work with file paths
- Ensures code works on Windows, Mac, and Linux

---

### **SECTION 2: Initialize Flask Application**

```python
app = Flask(__name__)
```
- Creates the Flask web application instance
- `__name__` helps Flask know where to look for resources

```python
CORS(app)
```
- Enables CORS on the Flask app
- Without this, the browser would block frontend requests to the backend

---

### **SECTION 3: Define File Paths**

```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```
**Breakdown:**
1. `__file__` = path to current file (app.py)
2. `os.path.abspath(__file__)` = absolute path (e.g., C:\project\backend\app.py)
3. `os.path.dirname(...)` = get parent directory (C:\project\backend)
4. `os.path.dirname(...) again` = go up one more level (C:\project)
5. **Result**: BASE_DIR points to the project root folder

```python
MODEL_PATH = os.path.join(BASE_DIR, "ml", "churn_model.pkl")
```
- Builds complete path: `C:\project\ml\churn_model.pkl`
- `os.path.join()` automatically uses correct slashes for the operating system

```python
SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")
DATA_PATH = os.path.join(BASE_DIR, "ml", "telco_churn.csv")
```
- Same logic for scaler and customer data files

---

### **SECTION 4: Load ML Models and Data**

```python
model = joblib.load(MODEL_PATH)
```
- Loads the trained Logistic Regression model from disk
- This model was trained in `analysis.py` and saved as a `.pkl` file

```python
scaler = joblib.load(SCALER_PATH)
```
- Loads the StandardScaler used during training
- **Critical**: Same scaler MUST be used for predictions to match training format

```python
df_customers = pd.read_csv(DATA_PATH)
```
- Loads the customer database into a pandas DataFrame
- DataFrame = table with rows (customers) and columns (attributes)

```python
df_customers['TotalCharges'] = pd.to_numeric(df_customers['TotalCharges'], errors='coerce')
```
**Breakdown:**
- `TotalCharges` column contains text that looks like numbers
- `pd.to_numeric()` converts text to actual numbers
- `errors='coerce'` = if conversion fails, set value to NaN (Not a Number)

```python
TOTAL_CHARGES_MEDIAN = df_customers['TotalCharges'].median()
```
- Calculates the middle value of all TotalCharges
- Used later to fill in missing values

---

### **SECTION 5: Define Feature Names**

```python
FEATURE_NAMES = [
    "SeniorCitizen",
    "tenure",
    # ... 28 more features
]
```
**Why this is CRITICAL:**
- The ML model expects exactly 30 features in this exact order
- During training, `pd.get_dummies()` created these features
- Must replicate same transformation for predictions

**How encoding works:**
- Original data: `gender = "Male"` → Becomes: `gender_Male = 1`
- Original data: `gender = "Female"` → Becomes: `gender_Male = 0`
- This is called "one-hot encoding"

---

### **SECTION 6: Homepage Endpoint**

```python
@app.route("/")
def home():
    return jsonify({"message": "Customer Retention Intelligence API is running!"})
```
**Breakdown:**
- `@app.route("/")` = Decorator that maps URL `/` to this function
- When user visits `http://127.0.0.1:5000/`, this function runs
- `jsonify()` converts Python dict to JSON response

---

### **SECTION 7: Prediction Endpoint (Main Logic)**

```python
@app.route("/predict", methods=["POST"])
def predict():
```
- Maps URL `/predict` to this function
- `methods=["POST"]` = only accept POST requests (not GET)
- POST is used because we're sending data (customer ID)

#### **STEP 7.1: Receive and Validate Input**

```python
data = request.get_json()
```
- Extracts JSON data from the request body
- Example: `{"customerID": "7590-VHVEG"}`

```python
if "customerID" not in data:
    return jsonify({"error": "customerID is required"}), 400
```
- Checks if customerID was provided
- `400` = HTTP status code for "Bad Request"

```python
customer_id = data["customerID"]
```
- Extracts the customer ID value

#### **STEP 7.2: Find Customer in Database**

```python
customer_row = df_customers[df_customers["customerID"] == customer_id]
```
**Breakdown:**
- `df_customers["customerID"] == customer_id` creates a True/False list
- `df_customers[...]` filters rows where condition is True
- Result: DataFrame with 0 or 1 matching rows

```python
if customer_row.empty:
    return jsonify({"error": "Customer ID not found"}), 404
```
- `404` = HTTP status code for "Not Found"

```python
customer_data = customer_row.iloc[0].copy()
```
- `.iloc[0]` = get the first (and only) row
- `.copy()` = create a copy to avoid modifying original data

#### **STEP 7.3: Prepare Features**

```python
customer_features = customer_data.drop(['customerID'])
```
- Remove customerID because ML model doesn't need it

```python
if 'Churn' in customer_features.index:
    customer_features = customer_features.drop(['Churn'])
```
- Remove Churn column if it exists (this is what we're predicting!)

```python
if pd.isna(customer_features['TotalCharges']):
    customer_features['TotalCharges'] = TOTAL_CHARGES_MEDIAN
else:
    customer_features['TotalCharges'] = float(customer_features['TotalCharges'])
```
- Fill missing TotalCharges with median value
- Convert to float for ML processing

#### **STEP 7.4: One-Hot Encoding**

```python
customer_df = pd.DataFrame([customer_features])
```
- Convert Series (single row) to DataFrame (required for encoding)

```python
customer_encoded = pd.get_dummies(customer_df, drop_first=True, dtype=int)
```
**Breakdown:**
- `pd.get_dummies()` = convert categorical text to binary columns
- `drop_first=True` = avoid redundancy (if not Male, must be Female)
- `dtype=int` = use 0 and 1 instead of True/False

**Example:**
- Input: `Contract = "Month-to-month"`
- Output: `Contract_One year = 0`, `Contract_Two year = 0`

#### **STEP 7.5: Align Features**

```python
customer_final = pd.DataFrame(0, index=[0], columns=FEATURE_NAMES)
```
- Create empty DataFrame with all 30 feature columns
- Initialize all values to 0

```python
for col in customer_encoded.columns:
    if col in FEATURE_NAMES:
        customer_final[col] = customer_encoded[col].values[0]
```
- Copy values from encoded data to final DataFrame
- Ensures we have exactly 30 features even if customer is missing some

```python
customer_final = customer_final[FEATURE_NAMES]
```
- Reorder columns to match training order (CRITICAL!)

#### **STEP 7.6: Scale and Predict**

```python
customer_scaled = scaler.transform(customer_final)
```
- Normalizes feature values using the same scaler from training
- Example: MonthlyCharges of $80 might become 0.45 after scaling

```python
prediction = model.predict(customer_scaled)[0]
```
- Runs ML model prediction
- Returns 0 (Stay) or 1 (Churn)
- `[0]` extracts the single prediction from array

```python
probability = model.predict_proba(customer_scaled)[0][1]
```
**Breakdown:**
- `predict_proba()` returns probability for each class
- Returns: `[[0.65, 0.35]]` means 65% Stay, 35% Churn
- `[0]` gets the first row
- `[1]` gets the second value (probability of Churn)

```python
prediction_text = "CHURN" if prediction == 1 else "STAY"
```
- Converts 0/1 to human-readable text

#### **STEP 7.7: Build Response**

```python
response = {
    "customerID": customer_id,
    "prediction": prediction_text,
    "churn_probability": probability,
    "gender": customer_data.get("gender", ""),
    # ... more fields
}
```
- Creates dictionary with all customer info and prediction
- `.get("gender", "")` = get gender, or empty string if missing

```python
return jsonify(response)
```
- Converts dictionary to JSON and sends to frontend

---

### **SECTION 8: Error Handling**

```python
except Exception as e:
    return jsonify({"error": str(e)}), 400
```
- Catches any unexpected errors
- Returns error message to frontend

---

### **SECTION 9: Start Server**

```python
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
```
**Breakdown:**
- `if __name__ == "__main__"` = only run if this file is executed directly
- `host="127.0.0.1"` = localhost (only accessible from this computer)
- `port=5000` = server runs on port 5000
- `debug=True` = shows detailed errors and auto-reloads on code changes

---

## 🔄 **COMPLETE REQUEST FLOW**

```
1. Frontend sends: POST /predict {"customerID": "7590-VHVEG"}
2. Backend receives request
3. Find customer in df_customers DataFrame
4. Extract customer features (gender, tenure, etc.)
5. Drop non-predictive columns (customerID, Churn)
6. Handle missing TotalCharges
7. Apply one-hot encoding (text → numbers)
8. Align to exactly 30 features in correct order
9. Scale features using saved scaler
10. Run ML model prediction
11. Get probability score
12. Build response with prediction + customer details
13. Send JSON response to frontend
```

---

## 🔑 **KEY CONCEPTS**

### **Why Scaling?**
- ML models work better when all features are on similar scales
- Example: Tenure (1-72 months) vs TotalCharges (18-8684)
- Scaling converts both to range like -2 to +2

### **Why Exact Feature Order?**
- ML model learns: "Feature 0 = SeniorCitizen, Feature 1 = tenure, ..."
- If order changes, model interprets wrong features

### **Why One-Hot Encoding?**
- ML models need numbers, not text
- "Male" and "Female" become 0 and 1
- "Month-to-month", "One year", "Two year" become multiple columns

---

## 📊 **DATA TRANSFORMATION EXAMPLE**

### Original Customer Data:
```
customerID: 7590-VHVEG
gender: Female
SeniorCitizen: 0
tenure: 1
Contract: Month-to-month
```

### After One-Hot Encoding:
```
SeniorCitizen: 0
tenure: 1
gender_Male: 0          (Female, so Male=0)
Contract_One year: 0    (Month-to-month, so both are 0)
Contract_Two year: 0
... 25 more features
```

### After Scaling:
```
SeniorCitizen: -0.43
tenure: -1.28
gender_Male: -1.00
Contract_One year: -0.65
Contract_Two year: -0.23
... 25 more features
```

### ML Model Output:
```
prediction: 0 (STAY)
probability: 0.431 (43.1% chance of churn)
```

---

This backend serves as the **bridge between the web interface and the ML model**, handling all data transformation, validation, and prediction logic! 🚀
