import cv2
import time
import numpy as np
import sys
from ultralytics import YOLO
from shapely.geometry import Point, Polygon
from tracker import StateManager
from emit import EventEmitter

""" Calculates the Homography matrix dynamically to map video coordinates to the 2D blueprint. """
def calc_matrix(vid_pts, map_pts):
    matrix, _ = cv2.findHomography(np.float32(vid_pts), np.float32(map_pts))
    return matrix

""" 2D Blueprint Zone Definitions """
STORE1_ZONES = {
    "ZONE_MAKEUP_UNIT": Polygon([(776, 555), (974, 550), (977, 244), (781, 236)]),
    "ZONE_NAIL_UNIT": Polygon([(597, 519), (447, 514), (602, 261), (445, 279)]),
    "BILLING_QUEUE_JOIN": Polygon([(1263, 460), (1492, 474), (1491, 250), (1254, 252)]),
    "ZONE_ACCESS_AREA": Polygon([(1411, 505), (1502, 611), (1497, 505), (1413, 613)]),
    "ZONE_MINIMALIST": Polygon([(764, 141), (906, 143), (905, 51), (765, 51)]),
    "ZONE_LOREAL": Polygon([(1091, 653), (1231, 646), (1235, 747), (1091, 750)]),
    "ZONE_ENTRY": Polygon([(36, 469), (200, 474), (200, 659), (16, 627)]),
    "ZONE_MENS": Polygon([(797, 651), (944, 645), (948, 748), (797, 750)])
}

STORE2_ZONES = {
    "ZONE_ENTRY": Polygon([(422, 1162), (569, 1160), (569, 1129), (422, 1130)]),
    "ZONE_WALL_LEFT": Polygon([(149, 663), (147, 1111), (94, 1119), (100, 659)]),
    "ZONE_WALL_RIGHT": Polygon([(834, 1113), (834, 643), (879, 642), (874, 1113)]),
    "ZONE_WALL_CASH": Polygon([(148, 628), (159, 668), (765, 665), (766, 630)]),
    "BILLING_QUEUE_JOIN": Polygon([(455, 741), (556, 744), (558, 650), (437, 644)]),
    "ZONE_MAKEUP_UNIT": Polygon([(606, 972), (725, 968), (718, 819), (602, 814)]),
    "ZONE_MK_GOND_1": Polygon([(289, 1000), (357, 927), (408, 989), (348, 1059)]),
    "ZONE_MK_GOND_2": Polygon([(309, 867), (375, 791), (331, 750), (258, 806)])
}

""" Master Camera Configurations """
CAM_CONFIGS = {
    "STORE1_CAM1": {
        "store_id": "ST1008", "cam_id": "CAM_01", "video": "CAM 1.mp4", "zones": STORE1_ZONES,
        "staff_lower": [0, 0, 0], "staff_upper": [180, 255, 60], "staff_thresh": 0.65,
        "matrix": calc_matrix([(1698, 935), (1831, 789), (1567, 602), (1416, 605)], [(776, 555), (974, 550), (977, 244), (781, 236)])
    },
    "STORE1_CAM2": {
        "store_id": "ST1008", "cam_id": "CAM_02", "video": "CAM 2.mp4", "zones": STORE1_ZONES,
        "staff_lower": [0, 0, 0], "staff_upper": [180, 255, 60], "staff_thresh": 0.65,
        "matrix": calc_matrix([(194, 892), (116, 687), (492, 503), (656, 644)], [(781, 521), (963, 523), (965, 266), (792, 259)])
    },
    "STORE1_CAM3": {
        "store_id": "ST1008", "cam_id": "CAM_03", "video": "CAM 3.mp4", "zones": STORE1_ZONES,
        "staff_lower": [0, 0, 0], "staff_upper": [180, 255, 60], "staff_thresh": 0.65,
        "matrix": calc_matrix([(899, 826), (1191, 474), (1395, 610), (1210, 992)], [(2, 438), (0, 612), (164, 655), (143, 423)])
    },
    "STORE1_CAM4": {
        "store_id": "ST1008", "cam_id": "CAM_04", "video": "CAM 4.mp4", "zones": STORE1_ZONES,
        "staff_lower": [0, 0, 0], "staff_upper": [180, 255, 60], "staff_thresh": 0.65,
        "matrix": calc_matrix([(337, 1040), (369, 454), (1297, 531), (1364, 1028)], [(1255, 252), (1252, 456), (1476, 455), (1478, 265)])
    },
    "STORE2_ENTRY1": {
        "store_id": "ST1009", "cam_id": "CAM_ENTRY_01", "video": "entry 1.mp4", "zones": STORE2_ZONES,
        "staff_lower": [140, 50, 50], "staff_upper": [170, 255, 255], "staff_thresh": 0.40,
        "matrix": calc_matrix([(306, 612), (645, 550), (670, 620), (309, 677)], [(422, 1162), (569, 1160), (569, 1129), (422, 1130)])
    },
    "STORE2_ENTRY2": {
        "store_id": "ST1009", "cam_id": "CAM_ENTRY_02", "video": "entry 2.mp4", "zones": STORE2_ZONES,
        "staff_lower": [140, 50, 50], "staff_upper": [170, 255, 255], "staff_thresh": 0.40,
        "matrix": calc_matrix([(305, 569), (655, 529), (664, 618), (308, 669)], [(422, 1162), (569, 1160), (569, 1129), (422, 1130)])
    },
    "STORE2_BILLING": {
        "store_id": "ST1009", "cam_id": "CAM_BILLING", "video": "billing_area.mp4", "zones": STORE2_ZONES,
        "staff_lower": [140, 50, 50], "staff_upper": [170, 255, 255], "staff_thresh": 0.40,
        "matrix": calc_matrix([(348, 1038), (335, 411), (642, 405), (674, 1040)], [(455, 741), (556, 744), (558, 650), (437, 644)])
    },
    "STORE2_ZONE": {
        "store_id": "ST1009", "cam_id": "CAM_ZONE", "video": "zone.mp4", "zones": STORE2_ZONES,
        "staff_lower": [140, 50, 50], "staff_upper": [170, 255, 255], "staff_thresh": 0.40,
        "matrix": calc_matrix([(467, 496), (858, 1040), (955, 79), (504, 3)], [(834, 1113), (834, 643), (879, 642), (874, 1113)])
    }
}

ACTIVE_CAM = sys.argv[1] if len(sys.argv) > 1 else "STORE1_CAM1"
CONFIG = CAM_CONFIGS[ACTIVE_CAM]

""" HSV Color Filtering to detect staff members based on active store uniform thresholds """
def is_staff(frame, box):
    x1, y1, x2, y2 = map(int, box)
    h_f, w_f = frame.shape[:2]
    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w_f, x2), min(h_f, y2)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0: return False

    h, w = crop.shape[:2]
    torso = crop[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
    if torso.size == 0: return False

    mask = cv2.inRange(
        cv2.cvtColor(torso, cv2.COLOR_BGR2HSV),
        np.array(CONFIG["staff_lower"]), np.array(CONFIG["staff_upper"])
    )
    return (cv2.countNonZero(mask) / (torso.shape[0] * torso.shape[1])) > CONFIG["staff_thresh"]

""" Main Video Processing Pipeline Initialization """
def run_pipeline():
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(CONFIG["video"])

    emitter = EventEmitter(api_url="http://localhost:8000/events/ingest", config=CONFIG)
    state_manager = StateManager(emitter=emitter)

    print(f"🚀 Live Detection Engine: {ACTIVE_CAM} | Store ID: {CONFIG['store_id']}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        now = time.time()
        state_manager.cleanup_memory(now)

        results = model.track(frame, classes=[0], conf=0.35, persist=True, verbose=False)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            t_ids = results[0].boxes.id.int().cpu().numpy()

            for box, yolo_id in zip(boxes, t_ids):
                staff_flag = is_staff(frame, box)

                x1, y1, x2, y2 = box
                fx, fy = int((x1 + x2) / 2), int(y2)

                mapped = cv2.perspectiveTransform(np.array([[[fx, fy]]], dtype=np.float32), CONFIG["matrix"])
                map_pt = Point(int(mapped[0][0][0]), int(mapped[0][0][1]))
                curr_zone = next((n for n, p in CONFIG["zones"].items() if p.contains(map_pt)), None)

                persisted_id = state_manager.process_detection(
                    yolo_id=yolo_id,
                    curr_zone=curr_zone,
                    staff_flag=staff_flag,
                    frame=frame,
                    box=box,
                    now=now
                )

                color = (0, 0, 255) if staff_flag else (0, 255, 0)
                lbl = f"STAFF_{persisted_id}" if staff_flag else f"VIS_{persisted_id}"
                cv2.circle(frame, (fx, fy), 5, color, -1)
                cv2.putText(frame, lbl, (fx - 20, int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        alerts = state_manager.get_active_alerts(now)
        for i, txt in enumerate(alerts):
            cv2.putText(frame, txt, (20, 40 + (i * 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)
            cv2.putText(frame, txt, (20, 40 + (i * 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("AuraTrack - Intelligence Engine", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_pipeline()
