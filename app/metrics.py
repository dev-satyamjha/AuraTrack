from fastapi import APIRouter
from .ingestion import EVENT_STORE

router = APIRouter()

""" Aggregates unique visitors, average dwell time, and current queue depth. Filters out staff. """
@router.get("/{store_id}")
def get_store_metrics(store_id: str):
    customer_events = [
        e for e in EVENT_STORE
        if e.get("store_id") == store_id and not e.get("is_staff", False)
    ]

    unique_visitors = set()
    total_dwell_ms = 0
    dwell_count = 0
    abandoned_count = 0
    completed_count = 0

    for event in customer_events:
        if "id_token" in event:
            unique_visitors.add(event["id_token"])
        if "track_id" in event:
            unique_visitors.add(str(event["track_id"]))

        if event.get("event_type") == "ZONE_DWELL":
            total_dwell_ms += event.get("dwell_ms", 0)
            dwell_count += 1

        if event.get("event_type") == "queue_abandoned":
            abandoned_count += 1
        elif event.get("event_type") == "queue_completed":
            completed_count += 1

    avg_dwell_seconds = (total_dwell_ms / dwell_count / 1000) if dwell_count > 0 else 0
    total_queue = abandoned_count + completed_count
    abandonment_rate = (abandoned_count / total_queue * 100) if total_queue > 0 else 0

    return {
        "store_id": store_id,
        "unique_visitors_today": len(unique_visitors),
        "avg_dwell_seconds": round(avg_dwell_seconds, 2),
        "queue_abandonment_rate": round(abandonment_rate, 2),
        "zero_purchase_store": len(unique_visitors) > 0 and completed_count == 0
    }
