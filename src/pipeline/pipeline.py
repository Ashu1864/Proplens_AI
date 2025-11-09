from prefect import flow, task
from loguru import logger
import camelot
import pdfplumber
import chromadb
import psycopg2
from psycopg2.extras import execute_values

from src.models.planning_costing_models import create_tables, get_session, CostItem
from src.models.planning_costing_transform_load import transform_table_to_cost_items, load_cost_items_to_db

# Paths to documents
PDF_SCHEDULE_PATH = "../data/Project-schedule-document.pdf"
PDF_REGULATORY_PATH = "../data/URA-Circular-on-GFA-area-definition.pdf"
PDF_FLOWCHART_PATH = "../data/construction-approvals-long-process-chart.pdf"
PDF_COSTING_PATH = "../data/Construction-planning-and-costing.pdf"

# PostgreSQL connection details for direct queries from schedule and regulatory extraction
POSTGRES_CONN_INFO = {
    "host": "localhost",
    "database": "data_engineer",
    "user": "yourusername",
    "password": "yourpassword"
}

@task
def extract_schedule_text_task(pdf_path):
    logger.info(f"Extracting text from schedule PDF {pdf_path}")
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_data.append(text)
    return extracted_data

@task
def load_schedule_text_task(text_pages):
    logger.info("Loading schedule text into PostgreSQL")
    conn = psycopg2.connect(**POSTGRES_CONN_INFO)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_schedule_text (
            id SERIAL PRIMARY KEY,
            page_text TEXT
        )
    """)
    conn.commit()
    records = [(text,) for text in text_pages]
    execute_values(cur, "INSERT INTO project_schedule_text (page_text) VALUES %s", records)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"Inserted {len(records)} pages of schedule text")

@task
def extract_regulatory_text_task(pdf_path):
    logger.info(f"Extracting text from regulatory circular PDF {pdf_path}")
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
    return all_text

@task
def load_regulatory_text_task(text):
    logger.info("Loading regulatory circular text into PostgreSQL")
    conn = psycopg2.connect(**POSTGRES_CONN_INFO)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS regulatory_circular_text (
            id SERIAL PRIMARY KEY,
            content TEXT
        )
    """)
    conn.commit()
    cur.execute("INSERT INTO regulatory_circular_text (content) VALUES (%s)", (text,))
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Inserted regulatory circular text")

@task
def extract_flowchart_text_task(pdf_path):
    logger.info(f"Extracting annotations from flowchart PDF {pdf_path}")
    annotations = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                annotations.append((i + 1, text))
    return annotations

@task
def load_flowchart_annotations_task(annotations):
    logger.info("Loading flowchart annotations into PostgreSQL")
    conn = psycopg2.connect(**POSTGRES_CONN_INFO)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flowchart_annotations (
            id SERIAL PRIMARY KEY,
            page_number INT,
            annotation TEXT
        )
    """)
    conn.commit()
    records = [(page_num, annotation) for page_num, annotation in annotations]
    execute_values(cur, "INSERT INTO flowchart_annotations (page_number, annotation) VALUES %s", records)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"Inserted {len(records)} flowchart annotations")

@task
def extract_costing_tables_task(pdf_path):
    logger.info(f"Extracting tables from costing PDF {pdf_path}")
    tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
    logger.info(f"Extracted {len(tables)} tables")
    return [table.df for table in tables]

@task
def transform_and_load_costing_data_task(tables):
    logger.info("Transforming and loading costing data")
    create_tables()  # Creates tables if not exist
    for table in tables:
        cost_items = transform_table_to_cost_items(table)
        load_cost_items_to_db(cost_items)
    logger.info("Costing data loaded successfully")

@flow(name="Complete Data Engineering Pipeline")
def data_pipeline():
    # Schedule extraction/load
    schedule_text = extract_schedule_text_task(PDF_SCHEDULE_PATH)
    load_schedule_text_task(schedule_text)
    
    # Regulatory circular extraction/load
    regulatory_text = extract_regulatory_text_task(PDF_REGULATORY_PATH)
    load_regulatory_text_task(regulatory_text)
    
    # Flowchart extraction/load
    flowchart_annotations = extract_flowchart_text_task(PDF_FLOWCHART_PATH)
    load_flowchart_annotations_task(flowchart_annotations)

    # Construction costing extraction/load
    costing_tables = extract_costing_tables_task(PDF_COSTING_PATH)
    transform_and_load_costing_data_task(costing_tables)

    logger.info("All documents processed successfully.")

if __name__ == "__main__":
    data_pipeline()
