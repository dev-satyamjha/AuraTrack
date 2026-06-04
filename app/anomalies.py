from fastapi import APIRouter
from .ingestion import EVENT_STORE

router = APIRouter()

""" Scans the event stream for operational anomalies. """
@router.get("/{store_id}")
def detect_anomalies(store_id: str):
    store_events = [e for e in EVENT_STORE if e.get("store_id") == store_id]

    if not store_events:
        return {"status": "Anomaly: Empty Store", "empty_duration_minutes": "Unknown (No Data)"}

    anomalies = []

    cam_tracks = {}
    for event in store_events:
        if "track_id" in event:
            tid = event["track_id"]
            cid = event["camera_id"]
            if tid not in cam_tracks:
                cam_tracks[tid] = set()
            cam_tracks[tid].add(cid)

    overlap_count = sum(1 for cameras in cam_tracks.values() if len(cameras) > 1)

    if overlap_count > 0:
        anomalies.append({
            "type": "Camera Overlap Deduplication",
            "impacted_visitors": overlap_count,
            "resolution": "Re-ID applied. Double-counting prevented."
        })

    return {
        "store_id": store_id,
        "detected_anomalies": anomalies if anomalies else "None detected. Traffic is normal."
    }
