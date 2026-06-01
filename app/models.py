from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime

class Event(SQLModel, table=True):
    """
    The core event emitted by the computer vision detection layer.
    Used for both API validation and Database schema.
    """
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
