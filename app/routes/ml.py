# app/routes/ml.py

import os
import pandas as pd
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from joblib import load

from app.schemas import FraudPredictionRequest, FraudPredictionResponse
# If you want to query the DB to find how often a patient_name has appeared, 
# you can import get_db and query your invoice table:
# from app.database import get_db
# from sqlalchemy.orm import Session

router = APIRouter(prefix="/fraud", tags=["fraud-detection"])

# Path to your saved pipeline
model_path = os.path.join("app", "medical_fraud_rf_model.joblib")
try:
    rf_pipeline = load(model_path)
except Exception as e:
    raise RuntimeError(f"Error loading model from {model_path}: {str(e)}")

def derive_features(request: FraudPredictionRequest) -> pd.DataFrame:
    """
    Convert the raw request data into the 7 columns that the pipeline expects.
    """
    # 1. Convert date_service -> year, month, day
    service_year = request.date_service.year
    service_month = request.date_service.month
    service_day = request.date_service.day

    # 2. For demonstration, let's set claim_amount_bin using the same bins:
    # [0, 5000, 10000, 20000] => labels: ['low', 'medium', 'high']
    # If outside 20k, we might say it's 'high' or handle differently.
    if request.claim_amount <= 5000:
        claim_amount_bin = 'low'
    elif request.claim_amount <= 10000:
        claim_amount_bin = 'medium'
    else:
        claim_amount_bin = 'high'

    # 3. For patient_claim_count, we typically want to see how many times 
    #    that patient_name has occurred in the DB. For now, let's assume it 
    #    is their nth visit. We'll just set a placeholder of 1 for demonstration.
    patient_claim_count = 1  # or get the real count from your DB

    # 4. Construct a single-row DataFrame with the exact columns:
    data = {
        'claim_amount': [request.claim_amount],
        'patient_claim_count': [patient_claim_count],
        'service_year': [service_year],
        'service_month': [service_month],
        'service_day': [service_day],
        'icd10_code': [request.diagnosis],
        'claim_amount_bin': [claim_amount_bin],
    }
    df = pd.DataFrame(data)
    return df

@router.post("/predict", response_model=FraudPredictionResponse)
def predict_fraud(request: FraudPredictionRequest):
    """
    Predict the likelihood of fraudulent claim using the RandomForest pipeline.
    """
    try:
        # Build a single-row DataFrame
        df_features = derive_features(request)

        # Predict using the pipeline
        y_pred = rf_pipeline.predict(df_features)
        # If you want probabilities:
        y_prob = rf_pipeline.predict_proba(df_features)

        # Our model was trained with label mapping: 0 = legit, 1 = fraud
        # Convert the numeric result back to a string
        pred_label_str = "fraudulent" if y_pred[0] == 1 else "legitimate"

        # Probability of the claim being fraudulent
        prob_fraud = float(y_prob[0][1])  # second element is class=1 (fraud)

        return FraudPredictionResponse(
            prediction_label=pred_label_str,
            prediction_prob_fraud=prob_fraud
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
