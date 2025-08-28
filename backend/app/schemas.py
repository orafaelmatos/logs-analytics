# schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict

class LogCreate(BaseModel):
    service: str = Field(..., min_length=1, pattern=r'^\S.*\S$|^\S$')
    level: str = Field(..., min_length=1, pattern=r'^\S.*\S$|^\S$')
    message: str = Field(..., min_length=1, pattern=r'^\S.*\S$|^\S$')
    timestamp: datetime
    metadata: Optional[Dict] = {}