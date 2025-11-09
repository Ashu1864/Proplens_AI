import pdfplumber
import re

# Update this list as you find more item names in your PDFs!
KNOWN_ITEM_NAMES = [
    "Bearing Pile",
    "Cross Beam Decking",
    "Decking",
    "Site Access Road",
    "Ground Improvement Work",
    "Civil work"
]

def is_item_line(line):
    for item in KNOWN_ITEM_NAMES:
        # Check for exact start or line contains item
        if line.strip().startswith(item) or line.strip() == item:
            return item
    return None

def extract_cost_items(pdf_path):
    items = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines = (page.extract_text() or "").splitlines()
            current_item = None
            block_lines = []
            for line in lines:
                item_name = is_item_line(line)
                if item_name:
                    # Process previous item block if present
                    if current_item and block_lines:
                        items.extend(parse_item_block(current_item, block_lines))
                    current_item = item_name
                    block_lines = []
                elif current_item:
                    block_lines.append(line)
            # Last block at end of page
            if current_item and block_lines:
                items.extend(parse_item_block(current_item, block_lines))
    return items

def parse_item_block(item_name, lines):
    text = " ".join(lines)
    # Quantity extraction: finds weight in tons or volume in m3
    quantity = None
    q_match = re.search(r"W=?\s*([\d,\.]+)t", text)
    if not q_match:
        q_match = re.search(r"Volume=([^=]+)=([\d,\.]+)m3", text)
        if q_match:
            quantity = q_match.group(2).replace(",", "")
    else:
        quantity = q_match.group(1).replace(",", "")
    
    # Unit price extraction
    unit_price_match = re.search(r"(\d[\d,]+)\s*yen per [tm3]+", text)
    unit_price = unit_price_match.group(1).replace(",", "") if unit_price_match else None

    results = []
    for typ in ["foreign cost", "local cost"]:
        cost_match = re.search(r"([\d,]+) yen[^\(]*\(" + typ + r"\)", text)
        if cost_match:
            total_cost = cost_match.group(1).replace(",", "")
            results.append({
                "item_name": item_name,
                "quantity": quantity,
                "unit_price_yen": unit_price,
                "total_cost_yen": total_cost,
                "cost_type": typ
            })
    return results
