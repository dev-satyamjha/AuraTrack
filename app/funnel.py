from fastapi import APIRouter
from datetime import datetime, timedelta
import pandas as pd
from .ingestion import EVENT_STORE

router = APIRouter()

""" Loads POS data and calculates conversion correlation using a 5-minute sliding time window. """
@router.get("/conversion/{store_id}")
def get_conversion_rate(store_id: str):
    try:
        pos_df = pd.read_csv("pos_transactions.csv")
        pos_df = pos_df[pos_df["store_id"] == store_id]
    except Exception:
        return {"error": "POS transaction file unavailable."}

    billing_events = [
        e for e in EVENT_STORE
        if e.get("event_type") == "queue_completed" and e.get("store_id") == store_id
    ]

    converted_visitors = 0
    total_billing_visitors = len(billing_events)

    if total_billing_visitors == 0:
        return {"store_id": store_id, "conversion_rate": 0.0, "total_transactions": len(pos_df)}

    for event in billing_events:
        try:
            exit_time = datetime.fromisoformat(event["queue_exit_ts"].replace("Z", "+00:00"))
            window_end = exit_time + timedelta(minutes=5)

            for _, row in pos_df.iterrows():
                tx_time_str = f"{row['order_date']} {row['order_time']}"
                tx_time = datetime.strptime(tx_time_str, "%d-%m-%Y %H:%M:%S").replace(tzinfo=exit_time.tzinfo)

                if exit_time <= tx_time <= window_end:
                    converted_visitors += 1
                    break
        except:
            continue

    rate = (converted_visitors / total_billing_visitors) * 100 if total_billing_visitors > 0 else 0

    return {
        "store_id": store_id,
        "total_queue_completions": total_billing_visitors,
        "matched_transactions": converted_visitors,
        "conversion_rate_percentage": round(rate, 2)
    }
