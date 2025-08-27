# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class LogCreate(BaseModel):
    service: str
    level: str
    message: str
    timestamp: datetime
    metadata: Optional[Dict] = {}