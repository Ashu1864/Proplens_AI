import pdfplumber
from loguru import logger

def extract_project_schedule_text(pdf_path):
    extracted_texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_texts.append(text)
    logger.info(f"Extracted {len(extracted_texts)} pages from {pdf_path}")
    return extracted_texts

if __name__ == "__main__":
    pdf_file = "../../data/Project-schedule-document.pdf"
    pages_text = extract_project_schedule_text(pdf_file)
    for i, text in enumerate(pages_text):
        print(f"--- Page {i+1} ---")
        print(text[:500])  # Print first 500 characters for brevity
