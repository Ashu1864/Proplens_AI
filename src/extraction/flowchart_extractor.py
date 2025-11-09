import pdfplumber
from loguru import logger

def extract_flowchart_annotations(pdf_path):
    annotations = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Extract all text elements, which might include captions, labels
            text = page.extract_text()
            if text:
                annotations.append((page_num, text))
    logger.info(f"Extracted annotations from flowchart at {pdf_path}")
    return annotations

if __name__ == "__main__":
    pdf_file = "../../data/construction-approvals-long-process-chart.pdf"
    annotations = extract_flowchart_annotations(pdf_file)
    for page_num, annotation_text in annotations:
        print(f"--- Page {page_num} ---")
        print(annotation_text)
