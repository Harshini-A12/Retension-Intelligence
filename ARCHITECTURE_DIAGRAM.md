# 🏗️ System Architecture & Flow Diagrams

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER BROWSER                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           FRONTEND (Client-Side)                      │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ index.html  │  │ script.js   │  │  style.css  │  │  │
│  │  │   Structure │  │   Logic     │  │   Design    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP POST /predict
                           │ JSON: {"customerID": "..."}
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK SERVER (Backend)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    app.py                             │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │  Receive    │  │  Process    │  │   Predict   │  │  │
│  │  │  Request    │→ │   Data      │→ │   Churn     │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Load Models & Data
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA & ML LAYER                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  CSV Data    │  │  Trained ML  │  │   Feature    │     │
│  │              │  │    Model     │  │   Scaler     │     │
│  │ telco_churn  │  │ churn_model  │  │  scaler.pkl  │     │
│  │    .csv      │  │    .pkl      │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│         7,043 customers    80.7% accuracy   Normalization  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Request-Response Flow

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: USER INTERACTION                                     │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ User enters: "7590-VHVEG"
                           │ User clicks: "ANALYZE CUSTOMER"
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: FRONTEND VALIDATION                                  │
│  • Check if input is not empty                               │
│  • Show loading spinner                                      │
│  • Disable button                                            │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP POST Request
                           │ URL: http://127.0.0.1:5000/predict
                           │ Body: {"customerID": "7590-VHVEG"}
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: BACKEND RECEIVES REQUEST                             │
│  • Flask route: @app.route("/predict")                       │
│  • Parse JSON body                                           │
│  • Extract customerID                                        │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 4: DATABASE LOOKUP                                      │
│  • Search in df_customers DataFrame                          │
│  • Find matching customer row                                │
│  • Extract: gender, tenure, services, etc.                   │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 5: FEATURE ENGINEERING                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Original Data:                                         │  │
│  │ gender="Female", tenure=1, Contract="Month-to-month"  │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ One-Hot Encoding:                                      │  │
│  │ gender_Male=0, tenure=1, Contract_One year=0, etc.    │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Align to 30 Features (exact order):                   │  │
│  │ [0, 1, 29.85, 29.85, 0, 1, 0, 0, ...]                │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Feature Scaling (StandardScaler):                     │  │
│  │ [-0.43, -1.28, -0.52, -0.98, -1.00, ...]            │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 6: ML PREDICTION                                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ model.predict(customer_scaled)                         │  │
│  │ → Returns: 0 (STAY) or 1 (CHURN)                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ model.predict_proba(customer_scaled)                   │  │
│  │ → Returns: [0.569, 0.431]                              │  │
│  │   (56.9% Stay, 43.1% Churn)                           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 7: BUILD RESPONSE                                       │
│  {                                                           │
│    "customerID": "7590-VHVEG",                              │
│    "prediction": "STAY",                                     │
│    "churn_probability": 0.431,                              │
│    "gender": "Female",                                       │
│    "tenure": 1,                                              │
│    "MonthlyCharges": 29.85,                                 │
│    "Contract": "Month-to-month",                            │
│    ... (15+ more fields)                                     │
│  }                                                           │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP Response (JSON)
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 8: FRONTEND RECEIVES RESPONSE                           │
│  • Parse JSON data                                           │
│  • Extract prediction and customer details                   │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 9: UPDATE UI                                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Customer Header: "7590-VHVEG"                          │  │
│  │ Badge: "LIKELY TO STAY" (green)                        │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Churn Probability: 43.1%                               │  │
│  │ Progress Bar: [████████░░░░] 43.1% width             │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Metrics: Tenure=1, Charges=₹29.85, Contract=M2M      │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Profile: Female, Not Senior, Has Partner, No Deps     │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Insight: ✓ "Customer appears stable"                  │  │
│  │ Green background, positive message                     │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Services: [Phone: No] [Internet: DSL] [Security: No] │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 10: USER SEES RESULTS                                   │
│  • Smooth scroll to results section                          │
│  • Hide loading spinner                                      │
│  • Re-enable button                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Data Transformation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ RAW CUSTOMER DATA (from CSV)                                │
├─────────────────────────────────────────────────────────────┤
│ customerID      : 7590-VHVEG                                │
│ gender          : Female                                     │
│ SeniorCitizen   : 0                                         │
│ Partner         : Yes                                        │
│ Dependents      : No                                         │
│ tenure          : 1                                          │
│ PhoneService    : No                                         │
│ MultipleLines   : No phone service                           │
│ InternetService : DSL                                        │
│ OnlineSecurity  : No                                         │
│ OnlineBackup    : Yes                                        │
│ DeviceProtection: No                                         │
│ TechSupport     : No                                         │
│ StreamingTV     : No                                         │
│ StreamingMovies : No                                         │
│ Contract        : Month-to-month                             │
│ PaperlessBilling: Yes                                        │
│ PaymentMethod   : Electronic check                           │
│ MonthlyCharges  : 29.85                                      │
│ TotalCharges    : 29.85                                      │
│ Churn           : No                                         │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Drop customerID & Churn
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ FEATURES FOR ML (19 attributes)                             │
├─────────────────────────────────────────────────────────────┤
│ gender, SeniorCitizen, Partner, Dependents, tenure,         │
│ PhoneService, MultipleLines, InternetService,               │
│ OnlineSecurity, OnlineBackup, DeviceProtection,             │
│ TechSupport, StreamingTV, StreamingMovies, Contract,        │
│ PaperlessBilling, PaymentMethod, MonthlyCharges,            │
│ TotalCharges                                                │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ pd.get_dummies()
                           │ (One-Hot Encoding)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ ENCODED FEATURES (30 columns)                               │
├─────────────────────────────────────────────────────────────┤
│ Column 0:  SeniorCitizen = 0                                │
│ Column 1:  tenure = 1                                        │
│ Column 2:  MonthlyCharges = 29.85                           │
│ Column 3:  TotalCharges = 29.85                             │
│ Column 4:  gender_Male = 0           (Female → 0)           │
│ Column 5:  Partner_Yes = 1           (Yes → 1)              │
│ Column 6:  Dependents_Yes = 0        (No → 0)               │
│ Column 7:  PhoneService_Yes = 0      (No → 0)               │
│ Column 8:  MultipleLines_No phone service = 1               │
│ Column 9:  MultipleLines_Yes = 0                            │
│ Column 10: InternetService_Fiber optic = 0 (DSL → 0)       │
│ Column 11: InternetService_No = 0                           │
│ Column 12: OnlineSecurity_No internet service = 0           │
│ Column 13: OnlineSecurity_Yes = 0                           │
│ Column 14: OnlineBackup_No internet service = 0             │
│ Column 15: OnlineBackup_Yes = 1                             │
│ ... (15 more columns for other services)                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ StandardScaler.transform()
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ SCALED FEATURES (ready for ML model)                        │
├─────────────────────────────────────────────────────────────┤
│ [-0.43, -1.28, -0.52, -0.98, -1.00, 1.01, -0.67, -0.90,   │
│  2.15, -0.46, -0.76, -0.27, -0.52, -0.41, -0.53, 2.44,    │
│  -0.51, -0.40, -0.52, -0.39, -0.52, -0.39, -0.52, -0.39,  │
│  -0.51, -0.23, 1.05, -0.34, 1.24, -0.39]                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ model.predict() & predict_proba()
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ ML MODEL OUTPUT                                             │
├─────────────────────────────────────────────────────────────┤
│ Prediction: 0 (STAY)                                        │
│ Probability: [0.569, 0.431]                                 │
│              ▲      ▲                                        │
│              │      └─ 43.1% Churn                          │
│              └─ 56.9% Stay                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Component Structure

```
frontend/index.html
│
├─── <head>
│    ├─── Meta tags (charset, viewport)
│    ├─── <title>
│    └─── <link> to style.css
│
└─── <body>
     │
     ├─── Background Glows (decorative)
     │
     ├─── <div class="app"> (main container)
     │    │
     │    ├─── <aside class="sidebar"> ──────────────┐
     │    │    ├─── Brand (logo + name)             │
     │    │    ├─── Separator line                  │
     │    │    └─── Info text                       │
     │    │                                          │
     │    └─── <main class="main"> ─────────────────┤
     │         │                                     │
     │         ├─── <header> (page title)           │
     │         │                                     │
     │         ├─── <section class="search">        │
     │         │    ├─── Search icon                │
     │         │    ├─── Input field (customerID)   │
     │         │    ├─── Analyze button             │
     │         │    └─── Hint text                  │
     │         │                                     │
     │         ├─── <div id="loading"> (hidden)     │
     │         │    └─── Spinner + text             │
     │         │                                     │
     │         ├─── <div id="errorBox"> (hidden)    │
     │         │                                     │
     │         ├─── <section id="resultSection">    │
     │         │    │                                │
     │         │    ├─── Customer Header            │
     │         │    │    ├─── ID display            │
     │         │    │    └─── Prediction badge      │
     │         │    │                                │
     │         │    ├─── Metrics Grid (4 cards)     │
     │         │    │    ├─── Probability           │
     │         │    │    ├─── Tenure                │
     │         │    │    ├─── Monthly Charges       │
     │         │    │    └─── Contract              │
     │         │    │                                │
     │         │    ├─── Insight Grid (2 panels)    │
     │         │    │    ├─── Customer Profile      │
     │         │    │    └─── AI Insight            │
     │         │    │                                │
     │         │    └─── Services Panel             │
     │         │                                     │
     │         └─── <section id="emptyState">       │
     │              └─── Initial message            │
     │                                               │
     └─── <script src="script.js">                  │
                                                     
Fixed Left Sidebar ────────────────────┘
Scrollable Main Content ───────────────┘
```

---

## 🔌 API Endpoint Structure

```
Flask Backend (app.py)
│
├─── GET /
│    └─── Returns: {"message": "API is running!"}
│         Status: 200 OK
│         Purpose: Health check
│
└─── POST /predict
     │
     ├─── Request:
     │    {
     │      "customerID": "7590-VHVEG"
     │    }
     │
     ├─── Success Response (200):
     │    {
     │      "customerID": "7590-VHVEG",
     │      "prediction": "STAY",
     │      "churn_probability": 0.431,
     │      "gender": "Female",
     │      "SeniorCitizen": 0,
     │      "Partner": "Yes",
     │      "Dependents": "No",
     │      "tenure": 1,
     │      "PhoneService": "No",
     │      "MultipleLines": "No phone service",
     │      "InternetService": "DSL",
     │      "OnlineSecurity": "No",
     │      "OnlineBackup": "Yes",
     │      "DeviceProtection": "No",
     │      "TechSupport": "No",
     │      "StreamingTV": "No",
     │      "StreamingMovies": "No",
     │      "Contract": "Month-to-month",
     │      "PaperlessBilling": "Yes",
     │      "PaymentMethod": "Electronic check",
     │      "MonthlyCharges": 29.85,
     │      "TotalCharges": 29.85
     │    }
     │
     ├─── Error Response (404):
     │    {
     │      "error": "Customer ID not found"
     │    }
     │
     └─── Error Response (400):
          {
            "error": "customerID is required"
          }
```

---

## 🧠 ML Model Architecture

```
                    INPUT LAYER
                 (30 features)
                        │
                        │ [0, 1, 29.85, ...]
                        │
                        ▼
         ┌──────────────────────────────┐
         │   LOGISTIC REGRESSION MODEL   │
         │                               │
         │  w₁x₁ + w₂x₂ + ... + w₃₀x₃₀  │
         │             +                 │
         │           bias                │
         │             │                 │
         │             ▼                 │
         │    Sigmoid Function           │
         │    σ(z) = 1/(1 + e⁻ᶻ)        │
         └──────────────────────────────┘
                        │
                        ▼
                   OUTPUT LAYER
                        │
           ┌────────────┴────────────┐
           ▼                         ▼
     P(Churn=0)                P(Churn=1)
       0.569                      0.431
      (56.9%)                    (43.1%)
           │                         │
           └────────────┬────────────┘
                        │
                        ▼
              Final Prediction: 0 (STAY)
              (Choose class with highest probability)
```

---

## 📊 File Dependency Graph

```
                    USER
                     │
                     ▼
          ┌──────────────────────┐
          │  frontend/index.html │
          └──────────┬───────────┘
                     │
          ┌──────────┼───────────┐
          │          │            │
          ▼          ▼            ▼
   frontend/    frontend/    frontend/
   style.css    script.js    (images)
                     │
                     │ HTTP POST
                     │
                     ▼
          ┌──────────────────────┐
          │   backend/app.py     │
          └──────────┬───────────┘
                     │
          ┌──────────┼───────────┐
          │          │            │
          ▼          ▼            ▼
    ml/telco_    ml/churn_    ml/scaler.
    churn.csv    model.pkl      pkl
        │            │            │
        │            │            │
        └────────────┴────────────┘
                     │
            Created by ml/analysis.py
            (Training script - run offline)
```

---

## ⚡ Performance Flow

```
Operation Timeline:
│
├─ 0ms    : User clicks button
├─ 1ms    : JS validates input
├─ 2ms    : HTTP request sent
├─ 50ms   : Backend receives request
├─ 51ms   : Find customer in DataFrame
├─ 52ms   : Feature engineering
├─ 53ms   : ML prediction
├─ 54ms   : Build JSON response
├─ 55ms   : Response sent
├─ 105ms  : Frontend receives data
├─ 106ms  : Parse JSON
├─ 107ms  : Update DOM elements
├─ 150ms  : Animations complete
└─ 200ms  : Smooth scroll complete

Total Time: ~200ms (0.2 seconds)
```

---

## 🔐 Security Flow

```
┌─────────────────────────────────────────┐
│ SECURITY CONSIDERATIONS                 │
├─────────────────────────────────────────┤
│                                         │
│ 1. Input Validation                     │
│    ✓ Check customerID not empty         │
│    ✓ Backend validates ID exists        │
│                                         │
│ 2. CORS Protection                      │
│    ✓ Flask-CORS enabled                 │
│    ✓ Only allowed origins               │
│                                         │
│ 3. Error Handling                       │
│    ✓ Try-catch blocks                   │
│    ✓ Graceful error messages            │
│    ✓ No sensitive data in errors        │
│                                         │
│ 4. Data Privacy                         │
│    ✓ No passwords/PII exposed           │
│    ✓ Read-only database access          │
│                                         │
│ 5. Production Recommendations           │
│    ⚠ Add authentication                 │
│    ⚠ Add rate limiting                  │
│    ⚠ Use HTTPS in production            │
│    ⚠ Validate all inputs                │
│    ⚠ Add request logging                │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🎯 State Management Flow

```
APPLICATION STATES:

┌─────────────┐
│   INITIAL   │ → Empty state visible
│    STATE    │   Results hidden
└──────┬──────┘   Loading hidden
       │          Error hidden
       │ User enters ID
       ▼
┌─────────────┐
│   LOADING   │ → Loading visible
│    STATE    │   Empty state hidden
└──────┬──────┘   Results hidden
       │          Button disabled
       │ API response
       ▼
┌─────────────┐
│   SUCCESS   │ → Results visible
│    STATE    │   Loading hidden
└──────┬──────┘   Empty state hidden
       │          Error hidden
       │ OR       Button enabled
       │
       ▼
┌─────────────┐
│    ERROR    │ → Error visible
│    STATE    │   Loading hidden
└──────┬──────┘   Results hidden
       │          Empty state hidden
       │ User retries
       │
       └──────────► Back to LOADING STATE
```

---

This architecture demonstrates a **clean separation of concerns** with frontend, backend, and ML layers working together seamlessly! 🚀
