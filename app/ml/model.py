import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np
from joblib import dump, load

# Load dataset
df = pd.read_csv("invoice_labels.csv")

# Feature Engineering
def preprocess_data(df):
    # Convert date to numerical features
    df['date_service'] = pd.to_datetime(df['date_service'])
    df['service_year'] = df['date_service'].dt.year
    df['service_month'] = df['date_service'].dt.month
    df['service_day'] = df['date_service'].dt.day
    
    # Create claim amount bins
    df['claim_amount_bin'] = pd.cut(df['claim_amount'],
                                   bins=[0, 5000, 10000, 20000],
                                   labels=['low', 'medium', 'high'])
    
    # Count patient occurrences (potential fraud pattern)
    df['patient_claim_count'] = df.groupby('patient_name')['patient_name'].transform('count')
    
    return df[['claim_amount', 'patient_claim_count', 
             'service_year', 'service_month', 'service_day',
             'icd10_code', 'claim_amount_bin']]

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', ['claim_amount', 'patient_claim_count',
                               'service_year', 'service_month', 'service_day']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['icd10_code', 'claim_amount_bin'])
    ])

# Model pipeline
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        class_weight='balanced',
        random_state=42
    ))
])

# Train-test split
X = preprocess_data(df)
y = df['label'].map({'legitimate': 0, 'fraudulent': 1})
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train and evaluate
model.fit(X_train, y_train)
dump(model, 'medical_fraud_rf_model.joblib')
print("Model saved as medical_fraud_rf_model.joblib")
y_pred = model.predict(X_test)

print("Test Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))