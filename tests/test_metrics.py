""" PROMPT: "Generate a pytest file to validate the FastAPI metrics endpoint. Inject dummy events into the EVENT_STORE and assert that events flagged with is_staff=True are completely ignored in the unique_visitors_today count." """
from fastapi.testclient import TestClient
from app.main import app
from app.ingestion import EVENT_STORE

client = TestClient(app)

""" Injects fake data and verifies the API filters out employees from store traffic counts. """
def test_metrics_strictly_exclude_staff():
    EVENT_STORE.clear()

    EVENT_STORE.append({"event_type": "zone_entered", "store_id": "ST_TEST", "is_staff": True, "track_id": 99})
    EVENT_STORE.append({"event_type": "zone_entered", "store_id": "ST_TEST", "is_staff": False, "track_id": 100})

    response = client.get("/metrics/ST_TEST")

    assert response.status_code == 200
    data = response.json()

    assert data["unique_visitors_today"] == 1
