from pydantic import BaseModel
from typing import Optional

""" Schema for Entry, Exit, and Re-entry events. """
class EntryEvent(BaseModel):
    event_type: str
    id_token: str
    store_code: str
    camera_id: str
    event_timestamp: str
    is_staff: bool
    gender_pred: str
    age_pred: int
    age_bucket: str
    is_face_hidden: bool
    group_id: Optional[str] = None
    group_size: Optional[int] = None

""" Schema for Zone Enter, Zone Exit, and Zone Dwell events. """
class ZoneEvent(BaseModel):
    event_type: str
    track_id: int
    store_id: str
    camera_id: str
    zone_id: str
    zone_name: str
    zone_type: str
    is_revenue_zone: str
    event_time: str
    zone_hotspot_x: float
    zone_hotspot_y: float
    gender: str
    age: int
    age_bucket: str
    dwell_ms: Optional[int] = None

""" Schema for Billing Queue Abandoned and Completed events. """
class QueueEvent(BaseModel):
    queue_event_id: str
    event_type: str
    track_id: int
    store_id: str
    camera_id: str
    zone_id: str
    zone_name: str
    zone_type: str
    is_revenue_zone: str
    queue_join_ts: str
    queue_served_ts: Optional[str] = None
    queue_exit_ts: str
    wait_seconds: int
    queue_position_at_join: int
    abandoned: bool
    zone_hotspot_x: float
    zone_hotspot_y: float
    gender: str
    age: int
    age_bucket: str

""" Schema for Legacy POS Transaction Data. """
class POSTransaction(BaseModel):
    order_id: int
    order_date: str
    order_time: str
    store_id: str
    product_id: int
    brand_name: str
    total_amount: float
