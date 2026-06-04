""" PROMPT: "Generate a pytest suite for the AuraTrack tracker.py StateManager. Write a test that proves the 30-second ZONE_DWELL event triggers correctly when a visitor stays in a zone, using a mock event emitter." """
import time
import numpy as np
from pipeline.tracker import StateManager

""" A mock emitter to intercept API calls during testing without hitting the network. """
class MockEmitter:
    def __init__(self):
        self.events = []

    def emit_event(self, track_id, evt_type, staff=False, zone_info=None, box=None, wait_sec=0, join_ts=None):
        self.events.append(evt_type)

""" Validates that standing in a zone for 31 seconds fires the ZONE_DWELL event. """
def test_dwell_timer_fires_after_30_seconds():
    mock_emitter = MockEmitter()
    state_manager = StateManager(emitter=mock_emitter)

    start_time = time.time()
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    dummy_box = [10, 10, 50, 50]

    state_manager.process_detection(
        yolo_id=1, curr_zone="ZONE_LOREAL", staff_flag=False,
        frame=dummy_frame, box=dummy_box, now=start_time
    )

    state_manager.process_detection(
        yolo_id=1, curr_zone="ZONE_LOREAL", staff_flag=False,
        frame=dummy_frame, box=dummy_box, now=start_time + 31
    )

    assert "ZONE_DWELL" in mock_emitter.events
