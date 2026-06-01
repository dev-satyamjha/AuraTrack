from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from typing import List
import csv
from datetime import datetime

from database import create_db_and_tables, get_session, engine
from models import Event, Transaction
from analytics import compute_store_metrics, compute_store_funnel

def load_csv_data():
    """Loads the POS CSV into the database on startup."""
    with Session(engine) as session:
        existing = session.exec(select(Transaction)).first()
        if existing:
            return

        try:
            with open("pos_transactions.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    txn = Transaction(
                        transaction_id=row.get("transaction_id", "TXN_" + str(datetime.now().timestamp())),
                        store_id=row.get("store_id", "ST1008"),
                        timestamp=datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")),
                        amount=float(row.get("amount", 0.0))
                    )
                    session.add(txn)
                session.commit()
                print("POS Data successfully loaded into the database.")
        except FileNotFoundError:
            print("Warning: pos_transactions.csv not found in app/ directory.")
        except Exception as e:
            print(f"Error loading CSV: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    load_csv_data()
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
    return compute_store_metrics(session, store_id)

@app.get("/stores/{store_id}/funnel")
async def get_funnel(store_id: str, session: Session = Depends(get_session)):
    return compute_store_funnel(session, store_id)
