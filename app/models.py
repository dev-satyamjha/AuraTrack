from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime

class Event(SQLModel, table=True):
    event_id: str = Field(primary_key=True)
    store_id: str = Field(index=True)
    camera_id: str
    visitor_id: str = Field(index=True)
    event_type: str = Field(index=True)
    timestamp: datetime = Field(index=True)

    zone_id: Optional[str] = None
    dwell_ms: int = Field(default=0)
    is_staff: bool = Field(default=False)
    confidence: float

    metadata_field: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

class Transaction(SQLModel, table=True):
    """Stores the POS data from the CSV"""
    transaction_id: str = Field(primary_key=True)
    store_id: str = Field(index=True)
    timestamp: datetime = Field(index=True)
    amount: float
