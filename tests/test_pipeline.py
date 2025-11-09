import pytest
from prefect import flow
from src.pipeline.pipeline import (
    extract_schedule_text_task,
    load_schedule_text_task,
    extract_costing_tables_task,
    transform_and_load_costing_data_task,
)
import pandas as pd

MOCK_SCHEDULE_PDF = "tests/test_files/sample_schedule.pdf"
MOCK_COSTING_PDF = "tests/test_files/sample_costing.pdf"

def test_extract_schedule_text_task():
    extracted = extract_schedule_text_task.run(MOCK_SCHEDULE_PDF)
    assert isinstance(extracted, list)
    assert len(extracted) > 0
    assert all(isinstance(page, str) for page in extracted)

def test_costing_pipeline_part(monkeypatch):
    def mock_camelot_read_pdf(pdf_path, flavor, pages):
        # Return a list containing one sample dataframe
        return [pd.DataFrame({
            'Description': ['Item1', 'Item2'],
            'Quantity': [10, 5],
            'Unit Price': [100, 150],
            'Total Price': [1000, 750]
        })]

    # Monkeypatch camelot.read_pdf to avoid real PDF dependency
    import camelot
    monkeypatch.setattr(camelot, "read_pdf", mock_camelot_read_pdf)
    
    tables = extract_costing_tables_task.run(MOCK_COSTING_PDF)
    assert isinstance(tables, list)
    assert len(tables) > 0
    # Transform and load functions expect a list of dataframes
    # Typically you'd mock DB session but here we just call to verify no exceptions
    transform_and_load_costing_data_task.run(tables)
