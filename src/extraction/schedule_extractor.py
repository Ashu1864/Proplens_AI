import camelot
from datetime import datetime

def parse_date(date_str):
    # Remove weekday if present
    parts = date_str.split()
    if len(parts) == 2:
        date_value = parts[1]
    else:
        date_value = date_str
    try:
        # Format: 1/11/06
        return datetime.strptime(date_value, "%m/%d/%y").date()
    except Exception:
        return None

def extract_project_tasks(pdf_path):
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
    tasks = []
    for table in tables:
        df = table.df
        # Start after header row
        for idx, row in df.iloc[1:].iterrows():
            # Defensive: skip if not a task row
            try:
                # Check for valid task_id (should be int)
                task_id = row[0]
                if not task_id.isdigit():
                    continue
                duration = row[2]
                duration_days = int(duration.split()[0]) if duration else None
                start_date = parse_date(row[3])
                finish_date = parse_date(row[4])
                task = {
                    "task_id": int(task_id),
                    "task_name": row[1],
                    "duration_days": duration_days,
                    "start_date": start_date,
                    "finish_date": finish_date
                }
                tasks.append(task)
            except Exception:
                continue
    return tasks
