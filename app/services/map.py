from thefuzz import process

# Top 15 Mappings
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
    "sprained ankle": "S93.409A"
}

def clean_text(text):
    # Basic cleanup: lowercase, remove extra spaces
    return " ".join(str(text).lower().strip().split())

def map_diagnosis(diagnosis_text):
    diagnosis_clean = clean_text(diagnosis_text)
    
    # Check exact match for top 15
    if diagnosis_clean in diagnosis_mapping:
        return diagnosis_mapping[diagnosis_clean]
    
    # Fuzzy match for other diagnoses (threshold=80)
    matched_term, score = process.extractOne(diagnosis_clean, diagnosis_mapping.keys())
    if score >= 80:
        return diagnosis_mapping[matched_term]
    
    # Default code for unmapped terms (e.g., "R69" for unknown illness)
    return "R69"