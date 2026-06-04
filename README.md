# AuraTrack - Retail Intelligence API 

> An end-to-end computer vision and analytics pipeline that tracks retail visitors, measures zone dwell times, and correlates billing queue events with legacy point-of-sale data to calculate real-time store conversion rates.

---

## 📑 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Tech Stack & Models](#-tech-stack--models)
- [Directory Structure](#-directory-structure)
- [Setup & Execution](#-setup--execution-in-5-commands)
- [System Verification](#-system-verification-steps)
- [Engineering Choices](#-engineering-trade-offs--choices)
- [AI-Assisted Development](#-ai-assisted-development)

---

## ✨ Features

- **Real-Time Visitor Tracking:** Detects and tracks retail visitors across multiple camera zones using YOLOv8 Nano + BoT-SORT.
- **Zone Dwell Analytics:** Measures how long visitors spend in defined store zones using 2D Homography mapping.
- **Billing Queue Correlation:** Matches queue abandonment/completion events against legacy POS `.csv` data to compute conversion rates.
- **Idempotent Event Ingestion:** Prevents duplicate metric inflation from network retries using hashed `id_token` tracking.
- **Live Terminal Dashboard:** Real-time TUI powered by `rich` - zero browser overhead, runs directly in the CLI.
- **Staff Filtering:** Detects and excludes staff uniforms via HSV color thresholding - no custom ML model required.
- **Automated Test Suite:** Full `pytest` coverage for pipeline logic, metric aggregation, and anomaly detection.
- **Fully Containerized:** One `docker compose up` starts the entire backend - no manual environment setup needed.

---

## 🏗 System Architecture

The system is divided into **three decoupled microservices** that communicate over HTTP:

```
┌─────────────────────────────┐       JSON Payloads       ┌──────────────────────────────┐
│   Intelligence Pipeline     │ ────────────────────────► │     Application API           │
│   pipeline/                 │                           │     app/  (FastAPI)           │
│                             │                           │                              │
│  • YOLOv8n detection        │                           │  • Idempotent ingestion      │
│  • BoT-SORT tracking        │                           │  • Real-time metric calc     │
│  • 2D Homography zones      │                           │  • POS CSV correlation       │
│  • HSV staff filtering      │                           │  • Anomaly detection         │
│  • Lightweight Re-ID        │                           │  • Swagger docs at /docs     │
└─────────────────────────────┘                           └──────────────┬───────────────┘
                                                                         │ HTTP polling
                                                          ┌──────────────▼───────────────┐
                                                          │     Edge Dashboard            │
                                                          │     dashboard.py  (TUI)       │
                                                          │                              │
                                                          │  • rich terminal UI          │
                                                          │  • Real-time metrics view    │
                                                          │  • Conversion funnel display │
                                                          └──────────────────────────────┘
```

### Architectural Journey & Key Pivots

The initial design considered 3D pose estimation and deep Re-ID networks (like OSNet) for cross-camera tracking. This was deliberately abandoned in favour of a **geometric + deterministic** approach for two reasons: edge hardware constraints and deployment simplicity.

**Two core pivots made:**

1. **2D Homography over 3D depth estimation** — OpenCV's Homography matrix maps video pixel coordinates directly onto a 2D floorplan polygon. It is computationally near-free and highly accurate for zone entry detection.
2. **HSV Color Histogram Re-ID over deep learning** — When a visitor leaves a camera, their color signature is cached. A simple mathematical correlation links them on reappearance, preventing double-counting without requiring a GPU.

---

## 🛠️ Tech Stack & Models

| Layer | Technology | Reason |
|---|---|---|
| **Object Detection** | YOLOv8 Nano (`yolov8n`) | 30+ FPS on standard hardware; no GPU required |
| **Multi-Object Tracking** | BoT-SORT (via Ultralytics) | Native occlusion handling; no extra dependency |
| **Zone Mapping** | OpenCV Homography | Near-zero compute cost; no depth sensor needed |
| **Cross-Camera Re-ID** | HSV Color Histogram | GPU-free; configurable per store via HSV values |
| **Staff Filtering** | HSV Color Thresholding | Avoids fine-tuning a custom YOLO model entirely |
| **API Framework** | FastAPI | Async, auto-generates Swagger UI at `/docs` |
| **Data Validation** | Pydantic | Strict schema + deterministic idempotency tokens |
| **Datastore** | In-Memory (`EVENT_STORE`) + JSONL logging | 0ms aggregation latency; no DB race conditions |
| **Dashboard** | Python `rich` (TUI) | Near-zero overhead; works on edge hardware |
| **Containerization** | Docker + Docker Compose | Single-command startup; no environment conflicts |
| **Dependency Management** | `uv` + `pyproject.toml` | Lightning-fast installs; modern Python tooling |
| **Testing** | `pytest` | Automated coverage for pipeline, metrics & anomalies |

---

## 📁 Directory Structure

```text
AuraTrack/
├── docker-compose.yml        
├── pyproject.toml            
├── pos_transactions.csv      
├── dashboard.py              
├── README.md
├── app/                      
│   ├── main.py               
│   ├── models.py             
│   ├── ingestion.py          
│   ├── metrics.py            
│   ├── funnel.py             
│   ├── anomalies.py          
│   └── health.py             
├── pipeline/                 
│   ├── detect.py             
│   ├── tracker.py            
│   ├── emit.py               
│   └── run.sh                
├── tests/
│   ├── test_pipeline.py      
│   ├── test_metrics.py       
│   └── test_anomalies.py     
└── docs/
    ├── DESIGN.md             
    └── CHOICES.md            
```

---

## 🚀 Setup & Execution in 5 Commands

Ensure **Docker** and **`uv`** are installed. If not, `pip` works as a fallback for Step 3.
> **Important Pre-requisite**: Ensure all video feeds are placed directly inside the `pipeline/` directory before executing the batch script.

```bash
# 1. Clone the repository and enter the directory
git clone https://github.com/dev-satyamjha/AuraTrack && cd AuraTrack

# 2. Launch the FastAPI backend in the background via Docker
docker compose up --build -d

# 3. Create a virtual environment and install all dependencies via pyproject.toml
uv sync

# 4. Verify the API logic using the automated Pytest suite
uv run pytest tests/

# 5. Execute the batch processing pipeline across all camera feeds
uv run bash pipeline/run.sh
```

> 👉 **Sample Output:** You can view a generated AI data payload in `pipeline/sample_output.json`.

---

## ✅ System Verification Steps

### 1. API Documentation & Idempotency

Once the API is live (after Step 2), open the interactive Swagger dashboard at:

👉 `http://localhost:8000/docs`

The `/events/ingest` endpoint uses strict idempotency — it hashes the `id_token` and `event_time` of each incoming payload and rejects duplicates via a `SEEN_EVENTS` set. This ensures that network retries from tracker nodes never inflate store traffic metrics.

---

### 2. Live Terminal Dashboard

To watch real-time metrics update as the pipeline processes video:

1. Open a **new terminal window** at the project root.
2. Run the dashboard:
   ```bash
   python dashboard.py
   ```
   > **Note:** You can pass a store ID dynamically, e.g., `python dashboard.py ST1009`. Defaults to `ST1008`.
3. As videos process during Step 5, the TUI will automatically refresh - displaying live zone metrics, queue depths, and conversion data.

---

### 3. POS Correlation (Funnel Analytics)

After the pipeline finishes, query the conversion endpoint in your browser or via Swagger UI:

```
GET /funnel/conversion/ST1008
```

The API evaluates a **5-minute sliding window** anchored to the moment a visitor abandoned or completed the billing queue, then cross-references it against `pos_transactions.csv` to output the final **Conversion Rate**.

---

## ⚙️ Engineering Trade-offs & Choices

### Model: YOLOv8 Nano + BoT-SORT

Heavier alternatives like Faster R-CNN or DeepSORT were ruled out early. Retail environments require consistent real-time throughput - YOLOv8n achieves 30+ FPS on standard CPUs, and BoT-SORT's built-in occlusion handling removes the need for an additional tracking library.

Staff filtering was kept **outside the ML model intentionally**. HSV color thresholding on bounding boxes detects staff uniforms without needing a custom-trained YOLO variant - a new store can be onboarded by simply updating the HSV config values.

### Schema: Pydantic + Deterministic Idempotency

Strict Pydantic models enforce payload integrity at the API boundary. Each event payload carries a deterministic `id_token` (hashed from `track_id` + timestamp) generated at the pipeline edge. The backend maintains a `SEEN_EVENTS` set to silently discard any replay - critical in a distributed store network where network blips cause tracker nodes to retry.

### Datastore: In-Memory + JSONL over PostgreSQL

A PostgreSQL container was explicitly avoided. In a hackathon/evaluation environment, adding a relational DB introduces startup race conditions - the API can crash if the DB hasn't finished initializing. The in-memory `EVENT_STORE` with JSONL disk logging achieves:
- **0ms aggregation latency**
- **Instant startup** - no connection pool warmup
- **No dependency failures** on the judges' machines

### Dashboard: Terminal UI over Web Dashboard 

AuraTrack targets edge hardware in retail stores where RAM and CPU are constrained. A web dashboard adds browser rendering overhead and requires a secondary server process. The `rich` TUI provides instantaneous data visualization at near-zero cost, directly proving the real-time pipeline connection without leaving the CLI.

---

## 🤖 AI-Assisted Development

Generative AI was used as a pair-programmer at specific points in the development lifecycle:

- **Temporal Logic:** Brainstorming the state-machine for `queue_abandoned` vs. `queue_completed` events, including edge cases where visitors stand near a billing zone without actually queuing.
- **Test Generation:** Creating `pytest` mock scenarios for Camera Overlap Deduplication anomalies and validating the 5-minute POS sliding window without needing large test datasets.
- **API Structure:** Structuring FastAPI into modular routers (`/metrics`, `/funnel`, `/anomalies`) to keep the codebase clean and production-ready rather than a single monolithic file.

---
