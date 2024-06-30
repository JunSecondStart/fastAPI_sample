from sqlalchemy import create_engine, Column, Integer, Float, String
from database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    param1 = Column(Float, index=True)
    param2 = Column(Float, index=True)
    param3 = Column(Float, index=True)
    name = Column(String, index=True)

