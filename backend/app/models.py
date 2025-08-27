# models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LogMetric(Base):
    __tablename__ = "log_metrics"
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String)
    level = Column(String)
    count = Column(Integer, default=1)
    timestamp = Column(DateTime)
