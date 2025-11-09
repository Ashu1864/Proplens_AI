import pdfplumber
from loguru import logger

def extract_regulatory_circular_text(pdf_path):
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Extract text considering layout for better accuracy in circulars
            text = page.extract_text()
            if text:
                all_text += f"\n--- Page {page_num} ---\n" + text
    logger.info(f"Extracted text from regulatory circular at {pdf_path}")
    return all_text

if __name__ == "__main__":
    pdf_file = "../../data/URA-Circular-on-GFA-area-definition.pdf"
    text = extract_regulatory_circular_text(pdf_file)
    print(text[:2000])  # Print first 2000 characters for overview
