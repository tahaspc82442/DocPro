# DocPro - Invoice Processing & Fraud Detection API

## Overview

DocPro is a FastAPI-based application designed for processing medical invoices, extracting relevant information using OCR, and predicting potential fraudulent claims using a trained RandomForest classifier.

## Features

- **OCR-Based Invoice Processing**: Extracts text from invoice images.
- **Automated Fraud Detection**: Uses a machine learning model to detect fraudulent claims.
- **REST API Endpoints**: Provides an API for uploading invoices and querying predictions.
- **Database Integration**: Stores extracted invoice details in a PostgreSQL database.
- **Dockerized Deployment**: Fully containerized for easy deployment.

---

## Project Structure

```
DocPro
├── temp
├── app
│   ├── models.py               # Database models
│   ├── database.py             # Database connection setup
│   ├── schemas.py              # Pydantic schemas for API requests and responses
│   ├── main.py                 # FastAPI application entry point
│   ├── routes                  # API routes
│   │   ├── invoices.py         # Invoice-related API endpoints
│   │   ├── ml.py               # Fraud detection API endpoints
│   ├── services                # Business logic services
│   │   ├── ocr.py              # OCR text extraction
│   │   ├── map.py              # ICD-10 diagnosis mapping
│   ├── ml                      # Machine learning model
│   │   ├── model.py            # RandomForest model training
│   │   ├── generate_data.py    # Data generation script
│   │   ├── loader.py           # OCR and feature extraction utilities
├── invoice_labels.csv          # Sample dataset
├── requirements.txt            # Python dependencies
└── docker-compose.yml           # Docker setup for deployment
```

---

## Setup Instructions

### 1️⃣ Prerequisites

Ensure you have the following installed:

- **Python 3.10+**
- **Docker & Docker Compose**
- **PostgreSQL (if running locally)**

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set Up Environment Variables

Create a `.env` file with the following:

```env
DATABASE_URL=postgresql://docuser:password@localhost/invoices
```

### 4️⃣ Run the Application

#### Without Docker

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### With Docker

```bash
docker-compose up -d
```

### 5️⃣ Access the API

- API Root: [http://localhost:8000/](http://localhost:8000/)
- Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc UI: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints

### **Invoice Processing**

#### Upload an Invoice (Image File)

**POST** `/invoices/upload`

```json
Response:
{
  "id": 1,
  "patient_name": "John Doe",
  "claim_amount": 12000.5,
  "diagnosis": "Hypertension",
  "date_of_service": "2023-06-15",
  "predicted_label": "fraudulent",
  "predicted_fraud_probability": 0.85
}
```

#### List Invoices

**GET** `/invoices/`

#### Predict Fraud on an Invoice

**POST** `/invoices/{invoice_id}/predict_fraud`

### **Fraud Detection**

#### Predict Fraud Manually

**POST** `/fraud/predict`

```json
Request:
{
  "patient_name": "John Doe",
  "date_service": "2023-06-15",
  "claim_amount": 12000.5,
  "diagnosis": "Hypertension"
}
Response:
{
  "prediction_label": "fraudulent",
  "prediction_prob_fraud": 0.85
}
```

---

## Deployment on AWS EC2

### 1️⃣ Build and Push AMD64 Docker Image (Locally)

```bash
docker buildx build --platform linux/amd64 -t tahaspc/docpro:latest .
docker push tahaspc/docpro:latest
```

### 2️⃣ Pull and Run on EC2

```bash
ssh ec2-user@<EC2_PUBLIC_IP>
docker pull tahaspc/docpro:latest
docker-compose up -d
```

### 3️⃣ Access the App

Visit:

```
http://<EC2_PUBLIC_IP>/docs
```

---

## Troubleshooting

### Check Running Containers

```bash
docker ps
```

### Check Logs

```bash
docker-compose logs -f
```

### Restart Application

```bash
docker-compose restart
```

### Remove Existing Container (if needed)

```bash
docker rm -f docpro_app
```

---

## 📌 Submission Guidelines

- **GitHub Repo:** Upload all code and docs to a public GitHub repository.
- **Documentation:** Include this README.
- **Loom Video (Optional):** Record a walkthrough explaining your solution.
- **Deployment Links:** Share AWS EC2 instance URL if hosted.

---

## License

MIT License. Feel free to use and improve this project!

---

## 🚀 Happy Coding! 🚀

