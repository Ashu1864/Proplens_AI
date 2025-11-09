from prefect import flow, task
import psycopg2

from src.extraction.schedule_extractor import extract_project_tasks
from src.extraction.planning_costing_extractor import extract_cost_items
from src.extraction.regulatory_extractor import extract_regulatory_rules
from src.extraction.semantic_extractor import semantic_embed_pdf
import chromadb
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)
PDF_SCHEDULE_PATH = "data/Project-schedule-document.pdf"
PDF_COSTING_PATH = "data/Construction-planning-and-costing.pdf"
PDF_REGULATORY_PATH = "data/URA-Circular-on-GFA-area-definition.pdf"
PDF_FLOWCHART_PATH = "data/construction-approvals-long-process-chart.pdf"

DB_CONFIG = dict(
    host="localhost",
    database="data_engineer",
    user="postgres",
    password="Shrutika2210"
)

@task
def extract_and_load_schedule_task():
    tasks = extract_project_tasks(PDF_SCHEDULE_PATH)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_tasks (
            task_id INTEGER PRIMARY KEY,
            task_name VARCHAR(255),
            duration_days INTEGER,
            start_date DATE,
            finish_date DATE
        )
    """)
    for task in tasks:
        cur.execute("""
            INSERT INTO project_tasks (task_id, task_name, duration_days, start_date, finish_date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (task_id) DO NOTHING
        """, (task['task_id'], task['task_name'], task['duration_days'], task['start_date'], task['finish_date']))
    conn.commit()
    cur.close()
    conn.close()

@task
def extract_and_load_cost_items_task():
    cost_items = extract_cost_items(PDF_COSTING_PATH)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cost_items (
            item_name VARCHAR(255),
            quantity NUMERIC,
            unit_price_yen NUMERIC,
            total_cost_yen NUMERIC,
            cost_type VARCHAR(50)
        )
    """)
    for item in cost_items:
        cur.execute("""
            INSERT INTO cost_items (item_name, quantity, unit_price_yen, total_cost_yen, cost_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (item['item_name'], item['quantity'], item['unit_price_yen'], item['total_cost_yen'], item['cost_type']))
    conn.commit()
    cur.close()
    conn.close()

@task
def extract_and_load_regulatory_rules_task():
    rules = extract_regulatory_rules(PDF_REGULATORY_PATH)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS regulatory_rules (
            rule_id VARCHAR(50) PRIMARY KEY,
            rule_summary TEXT,
            measurement_basis VARCHAR(255)
        )
    """)
    for rule in rules:
        cur.execute("""
            INSERT INTO regulatory_rules (rule_id, rule_summary, measurement_basis)
            VALUES (%s, %s, %s)
            ON CONFLICT (rule_id) DO NOTHING
        """, (rule['rule_id'], rule['rule_summary'], rule['measurement_basis']))
    conn.commit()
    cur.close()
    conn.close()

@task
def semantic_index_task():
    semantic_embed_pdf(PDF_SCHEDULE_PATH, "project_schedule")
    semantic_embed_pdf(PDF_COSTING_PATH, "planning_costing")
    semantic_embed_pdf(PDF_REGULATORY_PATH, "regulatory_rules")
    semantic_embed_pdf(PDF_FLOWCHART_PATH, "flowchart_annotations")

@flow
def data_pipeline():
    extract_and_load_schedule_task()
    extract_and_load_cost_items_task()
    extract_and_load_regulatory_rules_task()
    semantic_index_task()

if __name__ == "__main__":
    data_pipeline()
