from fastapi import APIRouter
from .ingestion import EVENT_STORE

router = APIRouter()

""" Returns API status and current memory load for orchestrated environments. """
@router.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "AuraTrack App Layer",
        "events_in_memory": len(EVENT_STORE)
    }
