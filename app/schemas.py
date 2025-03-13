# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel
from datetime import date
from typing import Optional

class InvoiceBase(BaseModel):
    patient_name: str
    claim_amount: float
    diagnosis: str
    date_of_service: str
    original_filename: str

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: int
    created_at: datetime
    predicted_label: Optional[str] = None
    predicted_fraud_probability: Optional[float] = None

    class Config:
        from_attributes = True  # replaces orm_mode = True
 # Replaces orm_mode = True
# app/schemas.py



class FraudPredictionRequest(BaseModel):
    patient_name: str
    date_service: date
    claim_amount: float
    diagnosis: str
    # If you want them to explicitly pass label bins or claim_count, you can. 
    # Otherwise, we infer them automatically in the route.

class FraudPredictionResponse(BaseModel):
    prediction_label: str
    prediction_prob_fraud: float
