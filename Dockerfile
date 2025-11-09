# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for pdf processing and Postgres client
RUN apt-get update && apt-get install -y \
    build-essential \
    libpoppler-cpp-dev \
    pkg-config \
    python3-dev \
    poppler-utils \
    wget \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src
COPY data ./data

# Expose Prefect UI port (if needed)
EXPOSE 4200

# Entry point command to run pipeline
CMD ["python", "src/pipeline/pipeline.py"]
