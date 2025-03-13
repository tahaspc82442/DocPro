# DocPro

DocPro is an API-based invoice processing and fraud detection system. It extracts information from medical invoices using OCR, processes the data, and applies a machine learning model to classify invoices as legitimate or fraudulent.

## Features
- Upload medical invoices (JPG, PNG) and extract relevant details using OCR
- Store extracted invoice details in a PostgreSQL database
- Predict fraudulent invoices using a trained RandomForestClassifier model
- FastAPI-based API for easy interaction

## Project Structure
```
DocPro
├── temp                    # Temporary storage for uploaded invoices
├── app                     # Main application folder
│   ├── models.py           # SQLAlchemy models for database
│   ├── database.py         # Database connection setup
│   ├── schemas.py          # Pydantic models for request validation
│   ├── routes/             # API route handlers
│   │   ├── ml.py           # Fraud detection endpoints
│   │   ├── invoices.py     # Invoice processing endpoints
│   ├── services/           # Supporting services
│   │   ├── ocr.py          # OCR processing logic
│   │   ├── map.py          # Diagnosis code mapping logic
│   ├── ml/                 # Machine learning related files
│   │   ├── model.py        # Training script for fraud detection
│   │   ├── generate_data.py # Data generation script
│   │   ├── loader.py       # Feature extraction from images
│   ├── main.py             # FastAPI main entry point
├── invoice_labels.csv      # Sample dataset with labeled invoices
├── requirements.txt        # Required Python dependencies
├── README.md               # Documentation
```

## Prerequisites
Make sure you have the following installed on your system:
- Python 3.10+
- PostgreSQL database
- Virtual environment (optional but recommended)

## Setup and Installation
### 1. Clone the Repository
```sh
git clone https://github.com/your-repo/docpro.git
cd docpro
```

### 2. Create and Activate a Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure the Database
Update the `DATABASE_URL` in `.env` or set it as an environment variable:
```sh
export DATABASE_URL="postgresql://docuser:password@localhost/invoices"
```
Make sure PostgreSQL is running and create the `invoices` database:
```sh
psql -U docuser -d postgres -c "CREATE DATABASE invoices;"
```

### 5. Initialize the Database
```sh
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 6. Run the FastAPI Server
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Access the API
Once the server is running, open the interactive API documentation:
- Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## API Endpoints
### Upload an Invoice
```http
POST /invoices/upload
```
**Request:** Multipart form-data with an image file.

**Response:** Extracted invoice details stored in the database.

### List All Invoices
```http
GET /invoices/
```

### Predict Fraud for an Invoice
```http
POST /fraud/predict
```
**Request Body:**
```json
{
  "patient_name": "John Doe",
  "date_service": "2024-03-13",
  "claim_amount": 15000,
  "diagnosis": "M54.5"
}
```
**Response:**
```json
{
  "prediction_label": "fraudulent",
  "prediction_prob_fraud": 0.87
}
```

## Training a New Model
To train a new fraud detection model, run:
```sh
python app/ml/model.py
```
The trained model will be saved as `app/medical_fraud_rf_model.joblib`.

## License
This project is licensed under the MIT License.

## Contributors
- **Mohd Taha Abbas** - [LinkedIn](www.linkedin.com/in/mohd-taha-abbas-19458212b)

