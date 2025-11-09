import pandas as pd
from src.models.planning_costing_models import get_session, CostItem

def transform_table_to_cost_items(df):
    # Example transformation logic - adjust column names based on your PDF tables
    cost_items = []
    for _, row in df.iterrows():
        item = CostItem(
            item_name=row.get('Description') or row.get('Item', ''),
            quantity=float(row.get('Quantity', 0)),
            unit_price=float(row.get('Unit Price', 0)),
            total_price=float(row.get('Total Price', 0))
        )
        cost_items.append(item)
    return cost_items

def load_cost_items_to_db(cost_items):
    session = get_session()
    session.add_all(cost_items)
    session.commit()
    session.close()
