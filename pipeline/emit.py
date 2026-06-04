import requests
import uuid
import time
import json
import hashlib
from datetime import datetime, timezone

class EventEmitter:
    """ Initializes the emitter with the target API URL and the active camera configuration. """
    def __init__(self, api_url, config):
        self.api_url = api_url
        self.config = config
        self.active_groups = {}
        self.last_entry_time = 0
        self.current_group_id = 1

    """ Generates deterministic demographic data based on the visitor track ID. """
    def get_demographics(self, track_id):
        hash_val = int(hashlib.md5(str(track_id).encode()).hexdigest(), 16)

        age = 18 + (hash_val % 45)
        gender = "M" if hash_val % 2 == 0 else "F"

        if age < 25: bucket = "18-24"
        elif age < 35: bucket = "25-34"
        elif age < 45: bucket = "35-44"
        elif age < 55: bucket = "45-54"
        else: bucket = "55+"

        return gender, age, bucket

    """ Builds the event payload based on event type and dispatches it to the API and local JSONL file. """
    def emit_event(self, track_id, evt_type, staff=False, zone_info=None, box=None, wait_sec=0, join_ts=None):
        track_id = int(track_id)
        now_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        gender, age, bucket = self.get_demographics(track_id)

        hx, hy = 0.0, 0.0
        if box is not None:
            x1, y1, x2, y2 = box
            hx = round(float((x1 + x2) / 2), 1)
            hy = round(float(y2), 1)

        payload = {}

        if evt_type in ["entry", "exit", "REENTRY"]:
            if evt_type in ["entry", "REENTRY"]:
                now_sec = time.time()
                if now_sec - self.last_entry_time < 3.0:
                    self.active_groups[track_id] = f"G_{self.current_group_id}"
                else:
                    self.current_group_id += 1
                    self.active_groups[track_id] = f"G_{self.current_group_id}"
                self.last_entry_time = now_sec

            grp_id = self.active_groups.get(track_id, None)
            payload = {
                "event_type": evt_type,
                "id_token": f"ID_{track_id}",
                "store_code": self.config["store_id"],
                "camera_id": self.config["cam_id"],
                "event_timestamp": now_ts,
                "is_staff": staff,
                "gender_pred": gender,
                "age_pred": age,
                "age_bucket": bucket,
                "is_face_hidden": False,
                "group_id": grp_id,
                "group_size": 2 if grp_id else None
            }

        elif evt_type in ["zone_entered", "zone_exited", "ZONE_DWELL"]:
            payload = {
                "event_type": evt_type,
                "track_id": track_id,
                "store_id": self.config["store_id"],
                "camera_id": self.config["cam_id"],
                "zone_id": zone_info,
                "zone_name": zone_info,
                "zone_type": "SHELF" if "WALL" in str(zone_info) else "DISPLAY",
                "is_revenue_zone": "Yes",
                "event_time": now_ts,
                "zone_hotspot_x": hx,
                "zone_hotspot_y": hy,
                "gender": gender,
                "age": age,
                "age_bucket": bucket
            }
            if evt_type == "ZONE_DWELL":
                payload["dwell_ms"] = 30000

        elif evt_type in ["queue_completed", "queue_abandoned"]:
            if join_ts:
                join_dt = datetime.fromtimestamp(join_ts, timezone.utc).isoformat().replace("+00:00", "Z")
            else:
                join_dt = now_ts

            payload = {
                "queue_event_id": str(uuid.uuid4()),
                "event_type": evt_type,
                "track_id": track_id,
                "store_id": self.config["store_id"],
                "camera_id": self.config["cam_id"],
                "zone_id": zone_info,
                "zone_name": "Billing Counter Queue",
                "zone_type": "BILLING",
                "is_revenue_zone": "Yes",
                "queue_join_ts": join_dt,
                "queue_served_ts": now_ts if evt_type == "queue_completed" else None,
                "queue_exit_ts": now_ts,
                "wait_seconds": wait_sec,
                "queue_position_at_join": 2,
                "abandoned": True if evt_type == "queue_abandoned" else False,
                "zone_hotspot_x": hx,
                "zone_hotspot_y": hy,
                "gender": gender,
                "age": age,
                "age_bucket": bucket
            }

        try:
            requests.post(self.api_url, json=[payload], timeout=1)
        except:
            pass

        with open(f"output_events_{self.config['store_id']}.jsonl", "a") as f:
            f.write(json.dumps(payload) + "\n")
            f.flush()

        print(f"🚨 EVENT EMITTED: Saved to output_events_{self.config['store_id']}.jsonl")
