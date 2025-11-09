import camelot
from loguru import logger

def extract_tables_from_costing_pdf(pdf_path):
    # Use camelot to extract tables; flavor 'stream' works well for stream-based tables
    tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
    logger.info(f"Extracted {len(tables)} tables from costing PDF")
    
    # Convert tables to list of dataframes or CSV strings as needed for transformation
    extracted_tables = []
    for idx, table in enumerate(tables):
        df = table.df  # pandas dataframe
        logger.info(f"Table {idx+1} shape: {df.shape}")
        extracted_tables.append(df)
    return extracted_tables

if __name__ == "__main__":
    pdf_file = "../../data/Construction-planning-and-costing.pdf"
    tables = extract_tables_from_costing_pdf(pdf_file)
    
    # Example: print first few rows of first table
    if tables:
        print(tables[0].head())
    else:
        print("No tables extracted.")
