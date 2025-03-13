import cv2
import pytesseract
import re
from app.services.map import *

def extract_text(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)




# def extract_invoice_details(text):
#     # Clean the text to handle line breaks consistently
#     # First, preserve important line breaks by adding markers
#     text = re.sub(r'\n', ' LINEBREAK ', text)
#     # Replace multiple spaces with a single space
#     cleaned_text = re.sub(r'\s+', ' ', text)
    
#     # --- Patient Name Extraction ---
#     # Try specific pattern first
#     name_pattern = re.search(r"Patient Name:?\s*([^:]+?)(?=\s*LINEBREAK|\s*Date|\s*Dato|\s*\$|\s*Claim|\s*Diagnosis|\s*Diagnsis|$)", cleaned_text, re.IGNORECASE)
    
#     # Fallback patterns if the specific one fails
#     name_patterns = [
#         r"(?:Patient|Customer|Client)\s*(?:Name|ID)?:\s*([\w\s\.\-]+?)(?=\s*LINEBREAK|\s*Date|\s*\$|\s*Claim|\s*Diagnosis|$)",
#         r"Name\s*(?:of\s*patient)?:\s*([\w\s\.\-]+?)(?=\s*LINEBREAK|\s*Date|\s*\$|\s*Claim|\s*Diagnosis|$)",
#         r"(?:^|\s)([\w\s\.\-]+)(?=\s*(?:DOB|Date of Birth))"
#     ]
    
#     patient_name = "Unknown"
#     if name_pattern:
#         patient_name = name_pattern.group(1).strip()
#     else:
#         for pattern in name_patterns:
#             match = re.search(pattern, cleaned_text, re.IGNORECASE)
#             if match:
#                 patient_name = match.group(1).strip()
#                 break
    
#     # --- Claim Amount Extraction ---
#     # Try specific pattern first
#     claim_pattern = re.search(r"Claim Amount\s*\$?(\d+(?:\.\d+)?)", cleaned_text, re.IGNORECASE)
    
#     # Fallback patterns if the specific one fails
#     claim_patterns = [
#         r"(?:Claim|Invoice|Bill|Total)\s*(?:Amount|Cost|Price)?:\s*\$?([\d,\.]+)",
#         r"Amount\s*(?:Due|Claimed|Charged):\s*\$?([\d,\.]+)",
#         r"Total\s*(?:Due|To Pay):\s*\$?([\d,\.]+)",
#         r"\$\s*([\d,\.]+)(?=\s*(?:total|due|claim|LINEBREAK|$))"
#     ]
    
#     claim_amount = 0.0
#     if claim_pattern:
#         claim_amount = float(claim_pattern.group(1))
#     else:
#         for pattern in claim_patterns:
#             match = re.search(pattern, cleaned_text, re.IGNORECASE)
#             if match:
#                 # Handle various number formats
#                 amount_str = match.group(1).replace(",", "")
#                 try:
#                     claim_amount = float(amount_str)
#                     break
#                 except ValueError:
#                     continue
    
#     # --- Diagnosis Extraction ---
#     # Try specific pattern with both correct and misspelled versions
#     diagnosis_pattern = re.search(r"Diagn(?:osis|sis)\s+([^:]+?)(?=\s*LINEBREAK|\s*Claim|\s*\$|\s*Date|$)", cleaned_text, re.IGNORECASE)
    
#     # Fallback patterns if the specific one fails
#     diagnosis_patterns = [
#         r"(?:Diagnosis|Condition|Medical Code|DX|ICD)(?:-?\d*)?:\s*([\w\s\.\-,\(\)\/&]+?)(?=\s*LINEBREAK|\s*Claim|\s*Date|$)",
#         r"(?:^|\s)DX:\s*([\w\s\.\-,\(\)\/&]+?)(?=\s*LINEBREAK|\s*Claim|\s*Date|$)",
#         r"(?:Medical|Health)\s*(?:Condition|Issue):\s*([\w\s\.\-,\(\)\/&]+?)(?=\s*LINEBREAK|\s*Claim|\s*Date|$)"
#     ]
    
#     diagnosis = "N/A"
#     if diagnosis_pattern:
#         diagnosis = diagnosis_pattern.group(1).strip()
#     else:
#         for pattern in diagnosis_patterns:
#             match = re.search(pattern, cleaned_text, re.IGNORECASE)
#             if match:
#                 diagnosis = match.group(1).strip()
#                 break
    
#     # --- Date of Service Extraction ---
#     # Try specific pattern with both "Date" and "Dato" typo
#     date_pattern = re.search(r"Dat(?:e|o) of Service:?\s*(\d{1,2}/\d{1,2}/\d{4})", cleaned_text, re.IGNORECASE)
    
#     # Fallback patterns if the specific one fails
#     date_patterns = [
#         r"(?:Date|Day)\s*(?:of|for)?\s*(?:Service|Visit|Treatment|Consultation):?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
#         r"(?:Service|Visit|Treatment|DOS)\s*(?:Date|Day):?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
#         r"(?:^|\s)(?:DOS|Date):?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})"
#     ]
    
#     date_of_service = "Unknown"
#     if date_pattern:
#         date_of_service = date_pattern.group(1)
#     else:
#         for pattern in date_patterns:
#             match = re.search(pattern, cleaned_text, re.IGNORECASE)
#             if match:
#                 date_str = match.group(1)
#                 # Standardize date format if needed
#                 date_parts = re.split(r'[\/\-\.]', date_str)
#                 if len(date_parts) == 3:
#                     # Handle common date formats: MM/DD/YYYY or DD/MM/YYYY
#                     if len(date_parts[2]) == 2:  # Two-digit year
#                         date_parts[2] = "20" + date_parts[2] if int(date_parts[2]) < 50 else "19" + date_parts[2]
#                     # Format as MM/DD/YYYY
#                     date_of_service = f"{date_parts[0].zfill(2)}/{date_parts[1].zfill(2)}/{date_parts[2]}"
#                 else:
#                     date_of_service = date_str
#                 break
    
#     return {
#         "patient_name": patient_name,
#         "claim_amount": claim_amount,
#         "diagnosis": map_diagnosis(clean_text(diagnosis)),
#         "date_of_service": date_of_service
#     }


def extract_invoice_details(text):
    """
    A robust parser that extracts:
    - patient_name
    - claim_amount
    - diagnosis
    - date_of_service
    
    by scanning the text line by line and looking for known keywords and patterns.
    """

    # 1) Normalize line endings, strip leading/trailing space on each line
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 2) Initialize default values
    patient_name = "Unknown"
    claim_amount = 0.0
    diagnosis    = "N/A"
    date_of_service = "Unknown"

    # 3) Prepare synonyms or triggers for each field
    patient_triggers   = ["patient", "client", "customer", "member", "subscriber", "patient name"]
    amount_triggers    = ["amount", "total", "cost", "price", "claim", "charge", "$"]
    diagnosis_triggers = ["diagnosis", "diagnsis", "condition", "dx", "icd", "problem"]
    date_triggers      = ["date", "date of service", "dos", "day of service"]

    # 4) Helper functions to parse from a line
    def parse_patient_name(line_text):
        """
        Extracts the name from a line that likely contains 'patient' or synonyms.
        Examples:
            'Patient: John Doe'
            'Patient John Doe'
            'Patient Name: Jane Q. Public'
        """
        # remove 'patient', 'name', etc. from the line
        # e.g. "Patient John Doe" -> "John Doe"
        # If the line includes a colon, we’ll take what's after it, otherwise skip the first word.
        # The regex below tries to remove the initial keywords.
        cleaned = re.sub(r"(?i)\b(patient|client|customer|member|subscriber|name)\b[:\s]*", "", line_text).strip()
        return cleaned

    def parse_claim_amount(line_text):
        """
        Extracts a float from the line if there's a currency pattern.
        """
        # Match something like $12,345.67 or 12345.67 (with or without comma)
        pattern = re.search(r"\$?\s*([\d,]+(\.\d+)?)(?![\d])", line_text)
        if pattern:
            amt_str = pattern.group(1).replace(",", "")
            try:
                return float(amt_str)
            except ValueError:
                pass
        return None

    def parse_diagnosis(line_text):
        """
        Extracts a diagnosis from a line that mentions 'diagnosis', 'dx', etc.
        Examples:
            'Diagnosis: Back Pain M545'
            'Dx M545, back issues'
        """
        # remove the triggers from the line
        # "Diagnosis: back pain" -> "back pain"
        cleaned = re.sub(r"(?i)\b(diagnosis|diagnsis|condition|dx|icd|problem)\b[:\s]*", "", line_text).strip()
        return cleaned if cleaned else None

    def parse_date(line_text):
        """
        Looks for a date in multiple formats:
          - YYYY-MM-DD
          - MM/DD/YYYY or M/D/YYYY
          - DD/MM/YYYY or D/M/YYYY
          - Possibly 2-digit year as well
        """
        # We’ll keep it straightforward with a few patterns:
        #   2028-08-15
        #   08/15/2028
        #   8/15/24  etc.
        # We'll return the first that matches
        patterns = [
            r"(\d{4}-\d{2}-\d{2})",           # 2024-08-10
            r"(\d{1,2}/\d{1,2}/\d{4})",       # 08/15/2028
            r"(\d{1,2}/\d{1,2}/\d{2})",       # 8/15/24
            r"(\d{4}/\d{1,2}/\d{1,2})",       # 2028/8/15
        ]
        for pat in patterns:
            match = re.search(pat, line_text)
            if match:
                return match.group(1)
        return None

    # 5) Main line-by-line loop
    for line in lines:
        line_lower = line.lower()

        # Check if it’s likely about “patient name”
        if any(trigger in line_lower for trigger in patient_triggers):
            extracted_name = parse_patient_name(line)
            if extracted_name and extracted_name != "":
                patient_name = extracted_name
                continue

        # Check if it’s likely about “claim amount”
        if any(trigger in line_lower for trigger in amount_triggers):
            extracted_amount = parse_claim_amount(line)
            if extracted_amount is not None:
                claim_amount = extracted_amount
                continue

        # Check if it’s likely about “diagnosis”
        if any(trigger in line_lower for trigger in diagnosis_triggers):
            extracted_diagnosis = parse_diagnosis(line)
            if extracted_diagnosis and extracted_diagnosis != "":
                diagnosis = extracted_diagnosis
                continue

        # Check if it’s likely about “date of service”
        if any(trigger in line_lower for trigger in date_triggers):
            extracted_date = parse_date(line)
            if extracted_date and extracted_date != "":
                date_of_service = extracted_date
                continue

    # 6) (Optional) Map or clean the diagnosis further
    # diagnosis = map_diagnosis(diagnosis)

    # 7) Return the dictionary
    return {
        "patient_name": patient_name,
        "claim_amount": claim_amount,
        "diagnosis": map_diagnosis(clean_text(diagnosis)),
        "date_of_service": date_of_service
    }


# if __name__ == "__main__":
#     for i in range(10):
#         text = extract_text(f"invoices/invoice_{i+1}.png")
#         print(text)
#         details = extract_invoice_details(text)
#         print(f"Invoice {i+1} Details:")
#         print(details)