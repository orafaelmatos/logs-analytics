# models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class LogMetric(Base):
    __tablename__ = "log_metrics"
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String)
    level = Column(String)
    count = Column(Integer, default=1)
    timestamp = Column(DateTime)
    log_metadata = Column(JSON, default={})
    
    def __init__(self, **kwargs):
        if 'count' not in kwargs:
            kwargs['count'] = 1
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f"<LogMetric(service='{self.service}', level='{self.level}', count={self.count}, timestamp='{self.timestamp}')>"
