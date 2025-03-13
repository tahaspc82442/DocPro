# import os
# import uuid
# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.orm import Session

# from ..database import get_db
# from .. import models, schemas  # <-- relative import of models and schemas
# from ..services.ocr import extract_text, extract_invoice_details

# router = APIRouter(prefix="/invoices", tags=["invoices"])

# @router.post("/upload", response_model=schemas.InvoiceResponse)
# async def upload_invoice(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     try:
#         file_ext = os.path.splitext(file.filename)[-1].lower()
#         if file_ext not in [".png", ".jpg", ".jpeg"]:
#             raise HTTPException(status_code=400, detail="Invalid file format")

#         temp_dir = "temp"
#         os.makedirs(temp_dir, exist_ok=True)
#         temp_path = f"{temp_dir}/{uuid.uuid4()}{file_ext}"

#         # Save the file to a temp directory
#         with open(temp_path, "wb") as buffer:
#             buffer.write(await file.read())

#         # Extract OCR text and invoice details
#         text = extract_text(temp_path)
#         details = extract_invoice_details(text)

#         # Remove the temp file
#         os.remove(temp_path)

#         # Create and persist the invoice record
#         db_invoice = models.Invoice(
#             **details,
#             original_filename=file.filename,
#             processed_text=text
#         )
#         db.add(db_invoice)
#         db.commit()
#         db.refresh(db_invoice)

#         return db_invoice

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}") from e

# @router.get("/", response_model=list[schemas.InvoiceResponse])
# def list_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return db.query(models.Invoice).offset(skip).limit(limit).all()


import os
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd

from ..database import get_db
from .. import models, schemas
from ..services.ocr import extract_text, extract_invoice_details

# 1) Import joblib and load your RandomForest pipeline
from joblib import load

router = APIRouter(prefix="/invoices", tags=["invoices"])

# Adjust to your actual path for the saved pipeline:
MODEL_PATH = "app/medical_fraud_rf_model.joblib"
try:
    rf_pipeline = load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Could not load model from {MODEL_PATH}: {str(e)}")

@router.post("/upload", response_model=schemas.InvoiceResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_ext = os.path.splitext(file.filename)[-1].lower()
        if file_ext not in [".png", ".jpg", ".jpeg"]:
            raise HTTPException(status_code=400, detail="Invalid file format")

        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = f"{temp_dir}/{uuid.uuid4()}{file_ext}"

        # Save the file to a temp directory
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # Extract OCR text and invoice details
        text = extract_text(temp_path)
        details = extract_invoice_details(text)

        # Remove the temp file
        os.remove(temp_path)

        # Create and persist the invoice record
        db_invoice = models.Invoice(
            **details,
            original_filename=file.filename,
            processed_text=text
        )
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)

        return db_invoice

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}") from e

@router.get("/", response_model=list[schemas.InvoiceResponse])
def list_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Invoice).offset(skip).limit(limit).all()


#
# 2) New endpoint to predict fraud on an existing invoice
#
@router.post("/{invoice_id}/predict_fraud", response_model=schemas.InvoiceResponse)
def predict_invoice_fraud(invoice_id: int, db: Session = Depends(get_db)):
    """
    Retrieve invoice by ID, run the RandomForest pipeline to predict fraud,
    and optionally store the prediction in the invoice record.
    """

    # A) Fetch the invoice from DB
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # B) Convert the invoice data into the columns your pipeline expects
    df_features = build_feature_dataframe(invoice, db)

    # C) Run prediction
    y_pred = rf_pipeline.predict(df_features)
    y_proba = rf_pipeline.predict_proba(df_features)

    # Suppose 0 = legitimate, 1 = fraudulent
    predicted_label = "fraudulent" if y_pred[0] == 1 else "legitimate"
    prob_fraud = float(y_proba[0][1])  # Probability of class=1 (fraud)

    # D) (Optional) Save result back to invoice table
    # Make sure your Invoice model & schemas have these fields.
    invoice.predicted_label = predicted_label
    invoice.predicted_fraud_probability = prob_fraud
    db.commit()
    db.refresh(invoice)

    return invoice


def build_feature_dataframe(invoice: models.Invoice, db: Session) -> pd.DataFrame:
    """
    Transform the invoice DB record into the 7 columns your pipeline was trained on:
    [
      'claim_amount',
      'patient_claim_count',
      'service_year',
      'service_month',
      'service_day',
      'icd10_code',
      'claim_amount_bin'
    ]
    """
    # 1) date_of_service -> parse year, month, day
    #    (Assuming date_of_service is a string like '2025-03-13')
    try:
        service_dt = datetime.strptime(invoice.date_of_service, "%Y-%m-%d")
    except (ValueError, TypeError):
        service_dt = datetime.now()  # fallback if no valid date is present

    service_year = service_dt.year
    service_month = service_dt.month
    service_day = service_dt.day

    # 2) claim_amount_bin
    claim_amount = invoice.claim_amount or 0.0
    if claim_amount <= 5000:
        claim_amount_bin = "low"
    elif claim_amount <= 10000:
        claim_amount_bin = "medium"
    else:
        claim_amount_bin = "high"

    # 3) patient_claim_count
    #    Count how many times we've seen this patient_name in the DB
    patient_claim_count = db.query(models.Invoice).filter(
        models.Invoice.patient_name == invoice.patient_name
    ).count()

    # 4) icd10_code from invoice.diagnosis
    icd10_code = invoice.diagnosis or "UNKNOWN"

    # 5) Build DataFrame for model
    data = {
        "claim_amount": [claim_amount],
        "patient_claim_count": [patient_claim_count],
        "service_year": [service_year],
        "service_month": [service_month],
        "service_day": [service_day],
        "icd10_code": [icd10_code],
        "claim_amount_bin": [claim_amount_bin]
    }
    return pd.DataFrame(data)

