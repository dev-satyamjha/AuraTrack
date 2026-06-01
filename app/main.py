from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="AuraTrack Intelligence API")

# Schemas
class EventPayload(BaseModel):
    event_id: str
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str
    timestamp: str
    zone_id: str | None = None
    dwell_ms: int = 0
    is_staff: bool = False
    confidence: float
    metadata: Dict[str, Any] = {}

# Endpoints 

@app.get("/health")
async def health_check():
    """Service status and stale feed warnings."""
    return {"status": "ok", "alerts": []}

@app.post("/events/ingest")
async def ingest_events(events: List[EventPayload]):
    """Accepts batches of up to 500 events."""
    return {"status": "success", "processed": len(events)}

@app.get("/stores/{store_id}/metrics")
async def get_metrics(store_id: str):
    """Returns today's core metrics."""
    return {
        "unique_visitors": 142,
        "conversion_rate": 0.15,
        "avg_dwell_time_seconds": 340,
        "queue_depth": 0,
        "abandonment_rate": 0.02,
        "data_confidence": True
    }

@app.get("/stores/{store_id}/funnel")
async def get_funnel(store_id: str):
    """Conversion funnel stats."""
    return {"entry": 142, "zone_visit": 120, "billing_queue": 30, "purchase": 21}

@app.get("/stores/{store_id}/heatmap")
async def get_heatmap(store_id: str):
    """Zone visit frequency normalized 0-100."""
    return {"SKINCARE": 85, "MAKEUP": 40, "FRAGRANCE": 10}

@app.get("/stores/{store_id}/anomalies")
async def get_anomalies(store_id: str):
    """Active anomalies like queue spikes."""
    return {"anomalies": []}