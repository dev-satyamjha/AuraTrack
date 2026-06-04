import cv2

class StateManager:
    """ Initializes the temporal memory buffers required for Re-ID and queue tracking. """
    def __init__(self, emitter):
        self.emitter = emitter
        self.state = {}
        self.seen = set()
        self.alerts = []
        self.id_map = {}
        self.exit_memory = []
        self.queue_join_times = {}
        self.last_dwell_emitted = {}

    """ Clears color histograms from memory if they are older than 10 minutes to prevent memory leaks. """
    def cleanup_memory(self, now):
        self.exit_memory = [m for m in self.exit_memory if now - m["time"] < 600]

    """ Extracts a normalized HSV color distribution from a bounding box for lightweight Re-ID. """
    def extract_histogram(self, frame, box):
        x1, y1, x2, y2 = map(int, box)
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return None

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return hist.flatten()

    """ Filters and returns active UI alerts for rendering on the video frame. """
    def get_active_alerts(self, now):
        self.alerts = [a for a in self.alerts if a["exp"] > now]
        return [a["txt"] for a in self.alerts]

    """ The core logic engine. Evaluates zone transitions, triggers API payloads, and maps IDs. """
    def process_detection(self, yolo_id, curr_zone, staff_flag, frame, box, now):
        persisted_id = self.id_map.get(yolo_id, yolo_id)
        lbl = f"STAFF_{persisted_id}" if staff_flag else f"VIS_{persisted_id}"

        if yolo_id not in self.seen and curr_zone == "ZONE_ENTRY":
            self.seen.add(yolo_id)
            hist = self.extract_histogram(frame, box)

            best_match, best_score = None, 0.75
            if hist is not None:
                for mem in self.exit_memory:
                    score = cv2.compareHist(hist, mem["hist"], cv2.HISTCMP_CORREL)
                    if score > best_score:
                        best_score, best_match = score, mem["orig_id"]

            if best_match:
                self.id_map[yolo_id] = best_match
                persisted_id = best_match
                self.emitter.emit_event(persisted_id, "REENTRY", staff_flag, box=box)
                self.alerts.append({"txt": f"REENTRY: {lbl}", "exp": now + 2})
                self.exit_memory = [m for m in self.exit_memory if m["orig_id"] != best_match]
            else:
                self.id_map[yolo_id] = yolo_id
                self.emitter.emit_event(yolo_id, "entry", staff_flag, box=box)
                self.alerts.append({"txt": f"ENTRY: {lbl}", "exp": now + 2})

        prev_zone = self.state.get(persisted_id)
        if curr_zone != prev_zone:
            if prev_zone:
                if "BILLING" in str(prev_zone):
                    join_t = self.queue_join_times.pop(persisted_id, now)
                    wait = int(now - join_t)
                    evt_name = "queue_completed" if wait > 5 else "queue_abandoned"
                    self.emitter.emit_event(persisted_id, evt_name, staff_flag, prev_zone, box=box, wait_sec=wait, join_ts=join_t)
                else:
                    self.emitter.emit_event(persisted_id, "zone_exited", staff_flag, prev_zone, box=box)

                hist = self.extract_histogram(frame, box)
                if hist is not None:
                    self.exit_memory.append({"orig_id": persisted_id, "hist": hist, "time": now})

            if curr_zone and curr_zone != "ZONE_ENTRY":
                if "BILLING" in str(curr_zone):
                    self.queue_join_times[persisted_id] = now
                else:
                    self.emitter.emit_event(persisted_id, "zone_entered", staff_flag, curr_zone, box=box)

                self.last_dwell_emitted[persisted_id] = now
                self.alerts.append({"txt": f"{curr_zone}: {lbl}", "exp": now + 2})

            self.state[persisted_id] = curr_zone

        if curr_zone and curr_zone != "ZONE_ENTRY" and "BILLING" not in str(curr_zone):
            if now - self.last_dwell_emitted.get(persisted_id, now) >= 30:
                self.emitter.emit_event(persisted_id, "ZONE_DWELL", staff_flag, curr_zone, box=box)
                self.last_dwell_emitted[persisted_id] = now

        return persisted_id
