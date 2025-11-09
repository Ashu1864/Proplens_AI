# Data Engineer Technical Challenge

This repository contains the solution for the Data Engineer Technical Challenge focused on extracting structured and unstructured data from real estate and construction documents.

## Project Overview

- Build a data pipeline using Prefect, Django, and Python.
- Extract data from provided construction and regulatory PDF documents.
- Store data in PostgreSQL (structured) and ChromaDB (vector database).
- Demonstrate pipeline orchestration and data ingestion robustness.

## Setup Instructions

1. Create and activate a Python virtual environment:
python3 -m venv venv
source venv/bin/activate

2. Install dependencies:

pip install -r requirements.txt


3. Configure PostgreSQL and ChromaDB locally.

4. Run the Prefect pipeline to extract and load data.

## Running Tests

Run tests using pytest:

pytest tests/


## Project Structure

- `src/` - Source code for extraction, pipeline, and database.
- `data/` - PDF files and intermediate data.
- `tests/` - Unit and integration tests.
- `docs/` - Project documentation.

## Author

Ashutosh Jasrotia