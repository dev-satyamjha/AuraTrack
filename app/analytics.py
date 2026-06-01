from sqlmodel import Session, select, func
from datetime import datetime
from models import Event

def compute_store_metrics(session: Session, store_id: str):
    """Computes real-time performance summary metrics for a store."""
    unique_visitors_query = select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id,
        Event.is_staff == False
    )
    unique_visitors = session.exec(unique_visitors_query).one() or 0

    dwell_query = select(func.avg(Event.dwell_ms)).where(
        Event.store_id == store_id,
        Event.event_type == "EXIT",
        Event.is_staff == False
    )
    avg_dwell_ms = session.exec(dwell_query).one()
    avg_dwell_sec = int((avg_dwell_ms / 1000)) if avg_dwell_ms else 0

    joined_queue = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id,
        Event.event_type == "BILLING_QUEUE_JOIN"
    )).one() or 0

    left_queue = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id,
        Event.event_type == "BILLING_QUEUE_LEAVE"
    )).one() or 0

    current_queue = max(0, joined_queue - left_queue)

    return {
        "unique_visitors": unique_visitors,
        "conversion_rate": 0.0,
        "avg_dwell_time_seconds": avg_dwell_sec,
        "queue_depth": current_queue,
        "abandonment_rate": 0.0,
        "data_confidence": True if unique_visitors > 0 else False
    }

def compute_store_funnel(session: Session, store_id: str):
    """Computes the step-by-step visitor dropdown counts."""
    entries = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id,
        Event.event_type == "ENTRY",
        Event.is_staff == False
    )).one() or 0

    zone_visits = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id,
        Event.event_type == "ZONE_ENTER",
        Event.is_staff == False
    )).one() or 0

    billing_queue = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id,
        Event.event_type == "BILLING_QUEUE_JOIN",
        Event.is_staff == False
    )).one() or 0

    return {
        "entry": entries,
        "zone_visit": zone_visits,
        "billing_queue": billing_queue,
        "purchase": 0
    }
