import pdfplumber
import re

def extract_regulatory_rules(pdf_path):
    rules = []

    q_pattern = re.compile(r"Q(\d+)\.\s*(.+)\n(.+)", re.DOTALL)  # Q1. Question \n Answer
    measurement_phrases = [
        "middle of the external wall",
        "edge of the covered area",
        "middle of such window and door components",
        "middle of the outermost vertical structures",
        "middle of the curtain wall",
        "middle of the wall"
    ]

    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

    # Find all Questions and Answers blocks
    q_blocks = list(re.finditer(r"(Q\d+\..+?)(?=Q\d+\.|$)", text, re.DOTALL))

    for q_block in q_blocks:
        block = q_block.group(1)
        lines = block.split("\n")
        header = lines[0]
        rule_id_match = re.match(r"(Q\d+)\.", header)
        if not rule_id_match:
            continue
        
        rule_id = rule_id_match.group(1).lower()
        rule_summary = header[len(rule_id)+2:].strip()
        answer_text = " ".join(lines[1:]).strip()
        measurement_basis = None
        for phrase in measurement_phrases:
            if phrase in answer_text:
                measurement_basis = phrase
                break

        # Fall back: try to extract a phrase after "measured up to the"
        if not measurement_basis:
            m = re.search(r"measured (.*?)[\.,]", answer_text)
            if m:
                measurement_basis = m.group(1).strip()

        rules.append({
            "rule_id": rule_id,
            "rule_summary": rule_summary,
            "measurement_basis": measurement_basis
        })

    return rules
