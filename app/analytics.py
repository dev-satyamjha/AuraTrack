from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from models import Event, Transaction

def get_converted_visitors(session: Session, store_id: str) -> int:
    """Finds visitors who were in the billing queue within 5 mins before a transaction."""
    transactions = session.exec(
        select(Transaction.timestamp).where(Transaction.store_id == store_id)
    ).all()

    if not transactions:
        return 0

    billing_events = session.exec(
        select(Event.visitor_id, Event.timestamp).where(
            Event.store_id == store_id,
            Event.event_type == "BILLING_QUEUE_JOIN",
            Event.is_staff == False
        )
    ).all()

    converted_visitors = set()

    for visitor_id, event_time in billing_events:
        for txn_time in transactions:
            time_diff = txn_time.replace(tzinfo=None) - event_time.replace(tzinfo=None)
            if timedelta(minutes=0) <= time_diff <= timedelta(minutes=5):
                converted_visitors.add(visitor_id)
                break

    return len(converted_visitors)

def compute_store_metrics(session: Session, store_id: str):
    unique_visitors = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id, Event.is_staff == False
    )).one() or 0

    avg_dwell_ms = session.exec(select(func.avg(Event.dwell_ms)).where(
        Event.store_id == store_id, Event.event_type == "EXIT", Event.is_staff == False
    )).one()
    avg_dwell_sec = int((avg_dwell_ms / 1000)) if avg_dwell_ms else 0

    joined_queue = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id, Event.event_type == "BILLING_QUEUE_JOIN"
    )).one() or 0

    left_queue = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id, Event.event_type == "BILLING_QUEUE_LEAVE"
    )).one() or 0
    current_queue = max(0, joined_queue - left_queue)

    converted_count = get_converted_visitors(session, store_id)
    conversion_rate = round(converted_count / unique_visitors, 2) if unique_visitors > 0 else 0.0

    return {
        "unique_visitors": unique_visitors,
        "conversion_rate": conversion_rate,
        "avg_dwell_time_seconds": avg_dwell_sec,
        "queue_depth": current_queue,
        "abandonment_rate": 0.0,
        "data_confidence": True if unique_visitors > 0 else False
    }

def compute_store_funnel(session: Session, store_id: str):
    entries = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id, Event.event_type == "ENTRY", Event.is_staff == False
    )).one() or 0

    zone_visits = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id, Event.event_type == "ZONE_ENTER", Event.is_staff == False
    )).one() or 0

    billing_queue = session.exec(select(func.count(func.distinct(Event.visitor_id))).where(
        Event.store_id == store_id, Event.event_type == "BILLING_QUEUE_JOIN", Event.is_staff == False
    )).one() or 0

    purchases = get_converted_visitors(session, store_id)

    return {
        "entry": entries,
        "zone_visit": zone_visits,
        "billing_queue": billing_queue,
        "purchase": purchases
    }
