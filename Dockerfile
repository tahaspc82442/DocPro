# Use a Python base image
FROM python:3.10

# Install tesseract and dependencies for OpenCV, Tesseract, etc.
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Copy only requirements first (for faster Docker build caching)
COPY requirements.txt /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire DocPro project into the container
COPY . /app

# By default, FastAPI runs on port 8000, so expose it
EXPOSE 8000

# (Optional) If you expect environment variables (like DATABASE_URL),
# you can define them here or pass them at runtime with `-e` flags:
# ENV DATABASE_URL=postgresql://docuser:password@your_rds_endpoint:5432/invoices

# Start FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
