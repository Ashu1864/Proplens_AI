from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class CostItem(Base):
    __tablename__ = 'cost_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)

def get_engine():
    return create_engine('postgresql://yourusername:yourpassword@localhost/data_engineer')

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
