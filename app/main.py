from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from contextlib import asynccontextmanager
from typing import List

from database import create_db_and_tables, get_session
from models import Event
from analytics import compute_store_metrics, compute_store_funnel

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="AuraTrack Intelligence API", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok", "alerts": []}

@app.post("/events/ingest")
async def ingest_events(events: List[Event], session: Session = Depends(get_session)):
    if len(events) > 500:
        raise HTTPException(status_code=413, detail="Batch size exceeds 500 events")

    processed = 0
    skipped = 0
    incoming_ids = [e.event_id for e in events]

    from sqlmodel import select
    existing_events = session.exec(
        select(Event.event_id).where(Event.event_id.in_(incoming_ids))
    ).all()
    existing_ids = set(existing_events)

    for event in events:
        if event.event_id not in existing_ids:
            session.add(event)
            processed += 1
        else:
            skipped += 1

    session.commit()
    return {"status": "success", "processed": processed, "skipped": skipped, "total_received": len(events)}

@app.get("/stores/{store_id}/metrics")
async def get_metrics(store_id: str, session: Session = Depends(get_session)):
    """Returns true real-time metric aggregations from the DB."""
    return compute_store_metrics(session, store_id)

@app.get("/stores/{store_id}/funnel")
async def get_funnel(store_id: str, session: Session = Depends(get_session)):
    """Returns true real-time conversion funnel drop-off metrics."""
    return compute_store_funnel(session, store_id)
