""" PROMPT: "Generate a pytest file for the anomaly detection API. Simulate a visitor (track_id: 1) being detected simultaneously by CAM1 and CAM2. Assert that the endpoint flags this as a Camera Overlap Deduplication event." """
from fastapi.testclient import TestClient
from app.main import app
from app.ingestion import EVENT_STORE

client = TestClient(app)

""" Verifies the anomaly engine detects when multiple cameras track the same ID, proving deduplication readiness. """
def test_camera_overlap_anomaly_detection():
    EVENT_STORE.clear()

    EVENT_STORE.append({"event_type": "zone_entered", "store_id": "ST_TEST", "track_id": 1, "camera_id": "CAM1"})
    EVENT_STORE.append({"event_type": "zone_entered", "store_id": "ST_TEST", "track_id": 1, "camera_id": "CAM2"})

    response = client.get("/anomalies/ST_TEST")

    assert response.status_code == 200
    data = response.json()

    detected_str = str(data["detected_anomalies"])
    assert "Camera Overlap Deduplication" in detected_str
    assert "impacted_visitors': 1" in detected_str
