from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer
from .database import Base

# app/models.py
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from .database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    claim_amount = Column(Float, nullable=False)
    diagnosis = Column(String, default="N/A")
    date_of_service = Column(String, default="Unknown")
    original_filename = Column(String, default="Unknown")
    processed_text = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    predicted_label = Column(String, nullable=True)
    predicted_fraud_probability = Column(Float, nullable=True)
