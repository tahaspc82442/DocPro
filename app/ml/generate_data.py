import os
import pandas as pd
from faker import Faker
import random
from thefuzz import process
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Create output directories
os.makedirs("invoices", exist_ok=True)

# Initialize Faker
fake = Faker()

# ================== DIAGNOSIS MAPPING ==================
diagnosis_mapping = {
    "hypertension": "I10",
    "type 2 diabetes": "E11.9",
    "asthma": "J45.909",
    "back pain": "M54.5",
    "acute upper respiratory infection": "J06.9",
    "major depressive disorder": "F32.9",
    "osteoarthritis": "M17.9",
    "copd": "J44.9",
    "migraine": "G43.909",
    "urinary tract infection": "N39.0",
    "anxiety disorder": "F41.9",
    "hyperlipidemia": "E78.5",
    "gerd": "K21.9",
    "seasonal allergies": "J30.9",
    "sprained ankle": "S93.409A",
    "routine checkup": "Z00.00"  # Added for fraud scenarios
}

diagnosis_variations = {
    "hypertension": ["hypertension", "high blood pressure", "htn", "elevated bp"],
    "type 2 diabetes": ["type 2 diabetes", "diabetes mellitus type 2", "dm2", "t2d"],
    "asthma": ["asthma", "chronic asthma", "asthma exacerbation"],
    "back pain": ["back pain", "lumbar pain", "lower back ache"],
    "acute upper respiratory infection": ["URI", "upper respiratory infection", "common cold", "acute URI"],  # ADDED
    "major depressive disorder": ["depression", "mdd", "clinical depression"],
    "osteoarthritis": ["osteoarthritis", "degenerative joint disease", "knee arthritis"],
    "copd": ["COPD", "chronic bronchitis", "emphysema"],
    "migraine": ["migraine", "migraine headache", "cephalgia"],
    "urinary tract infection": ["UTI", "urinary infection", "bladder infection"],
    "anxiety disorder": ["anxiety", "generalized anxiety disorder", "GAD"],
    "hyperlipidemia": ["high cholesterol", "hyperlipidemia", "elevated LDL"],
    "gerd": ["GERD", "acid reflux", "heartburn"],
    "seasonal allergies": ["hay fever", "allergic rhinitis", "seasonal allergies"],
    "sprained ankle": ["sprained ankle", "twisted ankle", "ankle injury"],
    "routine checkup": ["routine exam", "annual physical", "preventive checkup"]  # ADDED
}

# ================== FRAUD PARAMETERS ==================
FRAUD_PROVIDERS = set(fake.numerify(text="##########") for _ in range(50))  # 50 bad providers
PROCEDURE_DIAGNOSIS_MISMATCHES = {
    "99213": ["J06.9", "Z00.00"],  # Office visit for cold/checkup
    "93000": ["M54.5"],            # ECG for back pain
    "J3420": ["J30.9"]             # Vitamin injection for allergies
}

# ================== DATA GENERATION ==================
def map_diagnosis(diagnosis_text):
    diagnosis_clean = " ".join(str(diagnosis_text).lower().strip().split())
    if diagnosis_clean in diagnosis_mapping:
        return diagnosis_mapping[diagnosis_clean]
    matched_term, score = process.extractOne(diagnosis_clean, diagnosis_mapping.keys())
    return diagnosis_mapping[matched_term] if score >= 85 else "R69"

def generate_invoice(id):
    # Force 50% fraud base
    is_fraud = id % 2 == 0
    
    # Generate fraudulent pattern
    if is_fraud:
        diagnosis_key = random.choice(["back pain", "acute upper respiratory infection", "routine checkup"])
        diagnosis_text = random.choice(diagnosis_variations[diagnosis_key])
        claim_amount = round(random.uniform(12000, 20000), 2)
        provider_npi = random.choice(list(FRAUD_PROVIDERS))
        procedure_code = random.choice(list(PROCEDURE_DIAGNOSIS_MISMATCHES.keys()))
    else:
        diagnosis_key = random.choice(list(diagnosis_mapping.keys()))
        diagnosis_text = random.choice(diagnosis_variations[diagnosis_key])
        claim_amount = round(random.uniform(500, 10000), 2)
        provider_npi = fake.numerify(text="##########")
        procedure_code = random.choice(["99213", "93000", "90658", "J3420"])
    
    return {
        "invoice_id": id,
        "patient_name": fake.name(),
        "claim_amount": claim_amount,
        "diagnosis_text": diagnosis_text,
        "icd10_code": map_diagnosis(diagnosis_text),
        "date_service": fake.date_between(start_date="-2y", end_date="today"),
        "provider_npi": provider_npi,
        "procedure_code": procedure_code,
        "notes": random.choice(["", "Follow-up needed", "Urgent", "Lab pending"])
    }

# ================== LABELING & IMAGE GEN ==================
def assign_label(row):
    # Rule 1: High claim + minor diagnosis
    fraud_1 = (row["claim_amount"] > 10000) and (row["icd10_code"] in ["J06.9", "Z00.00", "M54.5"])
    
    # Rule 2: Procedure-diagnosis mismatch
    fraud_2 = row["icd10_code"] in PROCEDURE_DIAGNOSIS_MISMATCHES.get(row["procedure_code"], [])
    
    # Rule 3: Fraud provider network
    fraud_3 = row["provider_npi"] in FRAUD_PROVIDERS
    
    return "fraudulent" if fraud_1 or fraud_2 or fraud_3 else "legitimate"

def create_invoice_image(row):
    img = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    fields = [
        (50, 100, f"Patient: {row['patient_name']}"),
        (50, 130, f"Amount: ${row['claim_amount']:.2f}"),
        (50, 160, f"Diagnosis: {row['diagnosis_text']}"),
        (50, 190, f"ICD-10: {row['icd10_code']}"),
        (50, 220, f"Date: {row['date_service']}"),
        (50, 250, f"Provider: {row['provider_npi']}"),
        (50, 280, f"Procedure: {row['procedure_code']}"),
        (50, 310, f"Notes: {row['notes']}"),
    ]

    for x, y, text in fields:
        draw.text((x, y), text, font=font, fill="black")

    # Add noise
    if random.random() > 0.7:
        img = img.rotate(random.uniform(-1, 1))
    img.save(f"invoices/invoice_{row['invoice_id']}.png")
    return row

# ================== MAIN EXECUTION ==================
if __name__ == "__main__":
    # Generate dataset
    data = [generate_invoice(i) for i in range(20000)]
    df = pd.DataFrame(data)
    df["label"] = df.apply(assign_label, axis=1)
    
    # Force 50% balance if needed
    fraud_count = df["label"].value_counts().get("fraudulent", 0)
    if fraud_count < 10000:
        needed = 10000 - fraud_count
        legit_indices = df[df["label"] == "legitimate"].sample(needed).index
        df.loc[legit_indices, "label"] = "fraudulent"
    
    # Generate images
    print("Generating invoice images...")
    df = df.apply(create_invoice_image, axis=1)
    
    # Save metadata
    df["image_filename"] = df["invoice_id"].apply(lambda x: f"invoice_{x}.png")
    df.to_csv("invoice_labels.csv", columns=[
        "image_filename", "patient_name", "claim_amount", 
        "diagnosis_text", "icd10_code", "date_service",
        "provider_npi", "procedure_code", "notes", "label"
    ], index=False)
    
    print(f"Fraud distribution:\n{df['label'].value_counts(normalize=True)}")
    print("Dataset generation complete!")