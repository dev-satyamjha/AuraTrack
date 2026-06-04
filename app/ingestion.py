from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

EVENT_STORE = []
SEEN_EVENTS = set()

""" POST endpoint to accept event batches, evaluating idempotency to prevent duplicate ingestion. """
@router.post("/ingest")
def ingest_events(payload: List[Dict[str, Any]]):
    if len(payload) > 500:
        raise HTTPException(status_code=400, detail="Batch size exceeds 500 events limit.")

    ingested_count = 0

    for event in payload:
        event_id = event.get("queue_event_id") or event.get("id_token") or f"{event.get('track_id')}_{event.get('event_time')}"

        if event_id not in SEEN_EVENTS:
            SEEN_EVENTS.add(event_id)
            EVENT_STORE.append(event)
            ingested_count += 1

    return {
        "status": "success",
        "message": "Batch processed successfully.",
        "events_received": len(payload),
        "events_ingested": ingested_count
    }
