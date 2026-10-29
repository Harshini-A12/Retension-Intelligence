import pandas as pd

# ============================================================
# STEP 1 — Load the dataset
# ============================================================

df = pd.read_csv("telco_churn.csv")

print("Original dataset shape:")
print(df.shape)


# ============================================================
# STEP 2 — Remove customerID from ML features
# ============================================================

# customerID is only used to identify/search a customer.
# We don't want the ML model to use it for prediction.

df = df.drop("customerID", axis=1)


# ============================================================
# STEP 3 — Convert TotalCharges to numeric
# ============================================================

# TotalCharges is originally stored as text.
# Convert it into a numerical column.

df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"],
    errors="coerce"
)


# ============================================================
# STEP 4 — Handle missing values
# ============================================================

# Some TotalCharges values become NaN after conversion.
# Replace them with the median of TotalCharges.

df["TotalCharges"] = df["TotalCharges"].fillna(
    df["TotalCharges"].median()
)

print("\nMissing values after handling:")
print(df.isnull().sum())


# ============================================================
# STEP 5 — Separate Features (X) and Target (y)
# ============================================================

# X = customer information used for prediction
# y = what we want to predict

X = df.drop("Churn", axis=1)
y = df["Churn"]

print("\nFeatures (X):")
print(X.head())

print("\nTarget (y):")
print(y.head())


# ============================================================
# STEP 6 — Encode categorical features
# ============================================================

# Convert text/categorical columns into numerical columns.
# ML algorithms need numerical input.

X = pd.get_dummies(
    X,
    drop_first=True,
    dtype=int
)

print("\nX after encoding:")
print(X.head())

print("\nNumber of features after encoding:")
print(X.shape[1])

print("\nFeature names:")
print(X.columns.tolist())


# ============================================================
# STEP 7 — Convert target into numerical labels
# ============================================================

# No churn = 0
# Churn = 1

y = y.map({
    "No": 0,
    "Yes": 1
})

print("\nTarget after encoding:")
print(y.head())

print("\nTarget values:")
print(y.value_counts())


# ============================================================
# STEP 8 — Split data into training and testing sets
# ============================================================

from sklearn.model_selection import train_test_split

# 80% → Training data
# 20% → Testing data

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining data shape:")
print(X_train.shape)

print("\nTesting data shape:")
print(X_test.shape)

print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())

# ============================================================
# STEP 9 — Scale the features
# ============================================================

from sklearn.preprocessing import StandardScaler

# Create the scaler
scaler = StandardScaler()

# Learn scaling parameters from training data
X_train_scaled = scaler.fit_transform(X_train)

# Apply the same scaling to test data
X_test_scaled = scaler.transform(X_test)

print("\nFeature scaling completed!")

print("Scaled training data shape:")
print(X_train_scaled.shape)

print("Scaled testing data shape:")
print(X_test_scaled.shape)

# ============================================================
# STEP 10 — Train Logistic Regression
# ============================================================

from sklearn.linear_model import LogisticRegression

# Create the Logistic Regression model
logistic_model = LogisticRegression(max_iter=1000)

# Train using scaled training data
logistic_model.fit(X_train_scaled, y_train)

print("\nLogistic Regression model trained successfully!")

# ============================================================
# STEP 11 — Make predictions using Logistic Regression
# ============================================================

# Predict churn for the unseen test data
y_pred = logistic_model.predict(X_test_scaled)

print("\nPredicted churn values:")
print(y_pred[:20])

print("\nActual churn values:")
print(y_test.values[:20])

# ============================================================
# STEP 12 — Evaluate Logistic Regression
# ============================================================

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

# Calculate evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n==============================")
print("LOGISTIC REGRESSION RESULTS")
print("==============================")

print("Accuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)

print("\nConfusion Matrix:")
print(cm)

# Detailed report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ============================================================
# STEP 13 — Train Decision Tree
# ============================================================

from sklearn.tree import DecisionTreeClassifier

# Create Decision Tree model
decision_tree = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)

# Train the model
decision_tree.fit(X_train, y_train)

print("\nDecision Tree model trained successfully!")

# Make predictions
tree_pred = decision_tree.predict(X_test)

print("\nDecision Tree predictions:")
print(tree_pred[:20])

# ============================================================
# STEP 14 — Evaluate Decision Tree
# ============================================================

# Calculate evaluation metrics
tree_accuracy = accuracy_score(y_test, tree_pred)
tree_precision = precision_score(y_test, tree_pred)
tree_recall = recall_score(y_test, tree_pred)
tree_f1 = f1_score(y_test, tree_pred)

print("\n==============================")
print("DECISION TREE RESULTS")
print("==============================")

print("Accuracy :", tree_accuracy)
print("Precision:", tree_precision)
print("Recall   :", tree_recall)
print("F1 Score :", tree_f1)

# Confusion Matrix
tree_cm = confusion_matrix(y_test, tree_pred)

print("\nConfusion Matrix:")
print(tree_cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, tree_pred))

# ============================================================
# STEP 15 — Train Random Forest
# ============================================================

from sklearn.ensemble import RandomForestClassifier

# Create Random Forest model
random_forest = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train the model
random_forest.fit(X_train, y_train)

print("\nRandom Forest model trained successfully!")

# Make predictions
rf_pred = random_forest.predict(X_test)

print("\nRandom Forest predictions:")
print(rf_pred[:20])

# ============================================================
# STEP 16 — Evaluate Random Forest
# ============================================================

rf_accuracy = accuracy_score(y_test, rf_pred)
rf_precision = precision_score(y_test, rf_pred)
rf_recall = recall_score(y_test, rf_pred)
rf_f1 = f1_score(y_test, rf_pred)

print("\n==============================")
print("RANDOM FOREST RESULTS")
print("==============================")

print("Accuracy :", rf_accuracy)
print("Precision:", rf_precision)
print("Recall   :", rf_recall)
print("F1 Score :", rf_f1)

# Confusion Matrix
rf_cm = confusion_matrix(y_test, rf_pred)

print("\nConfusion Matrix:")
print(rf_cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, rf_pred))

# ============================================================
# STEP 17 — Compare All Models
# ============================================================

print("\n==============================")
print("MODEL COMPARISON")
print("==============================")

print("\nLogistic Regression:")
print("Accuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)

print("\nDecision Tree:")
print("Accuracy :", tree_accuracy)
print("Precision:", tree_precision)
print("Recall   :", tree_recall)
print("F1 Score :", tree_f1)

print("\nRandom Forest:")
print("Accuracy :", rf_accuracy)
print("Precision:", rf_precision)
print("Recall   :", rf_recall)
print("F1 Score :", rf_f1)

# ============================================================
# STEP 18 — Select Final Model
# ============================================================

final_model = logistic_model

print("\n==============================")
print("FINAL MODEL")
print("==============================")

print("Final model: Logistic Regression")
print("Accuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)

# ============================================================
# STEP 19 — Save the trained model and scaler
# ============================================================

import joblib

# Save the final ML model
joblib.dump(final_model, "churn_model.pkl")

# Save the scaler
joblib.dump(scaler, "scaler.pkl")

print("\nModel and scaler saved successfully!")

# ============================================================
# STEP 20 — Test the saved model with a new customer
# ============================================================

# Load the saved model and scaler
loaded_model = joblib.load("churn_model.pkl")
loaded_scaler = joblib.load("scaler.pkl")

# Take one customer from the test dataset
new_customer = X_test.iloc[[0]]

# Scale the customer using the SAME scaler used during training
new_customer_scaled = loaded_scaler.transform(new_customer)

# Predict churn
prediction = loaded_model.predict(new_customer_scaled)

# Get churn probability
probability = loaded_model.predict_proba(new_customer_scaled)

print("\n==============================")
print("NEW CUSTOMER PREDICTION")
print("==============================")

if prediction[0] == 1:
    print("Prediction: Customer is likely to CHURN")
else:
    print("Prediction: Customer is likely to STAY")

print("Churn probability:", probability[0][1])