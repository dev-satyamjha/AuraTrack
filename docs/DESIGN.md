# AuraTrack: System Architecture & Design Journey

## The Journey & Architectural Pivots
When designing AuraTrack, the primary goal was to build a retail analytics pipeline that was both highly accurate and capable of running on lightweight edge hardware (like an in-store computer). 

**Initial Approach:** My first instinct was to use heavy deep-learning models for 3D pose estimation and complex Re-ID (Re-Identification) networks (like OSNet) to track people across cameras. 

**The Pivot:** I quickly realized this was over-engineered. Heavy models would drop the frame rate and require expensive GPUs. I pivoted to a geometric and deterministic approach:
1.  **2D Homography:** Instead of 3D depth estimation, I used OpenCV to calculate a Homography matrix. This maps the video pixel coordinates directly onto a 2D floorplan polygon. It is computationally virtually free and highly accurate for identifying zone entries.
2.  **Lightweight Re-ID:** Instead of deep learning for camera handoffs, I implemented an HSV Color Histogram extractor. When a visitor leaves a camera, their color signature is temporarily cached. If they reappear, a simple mathematical correlation links them, preventing double-counting without the GPU overhead.

## System Architecture
The system is divided into three decoupled microservices:

1.  **The Intelligence Pipeline (`pipeline/`):** A Python OpenCV/YOLOv8 process that consumes video frames, maps coordinates to store zones, evaluates temporal logic (e.g., 30-second dwell times), and emits standard JSON payloads.
2.  **The Application API (`app/`):** A FastAPI backend that acts as the data warehouse and correlation engine. It ingests the telemetry, handles idempotency, calculates real-time metrics, and correlates queue completions with legacy POS `.csv` data.
3.  **The Edge Dashboard (`dashboard.py`):** A lightweight Terminal User Interface (TUI) utilizing the `rich` library. It polls the API endpoints in real-time, providing an immediate, resource-efficient view of store conversion funnels without requiring web-browser overhead.

## AI-Assisted Decisions
Generative AI was utilized as a pair-programmer during the development lifecycle:
* **Temporal Logic Design:** AI was used to brainstorm the state-machine logic for the `queue_abandoned` vs. `queue_completed` events, ensuring we accurately handled edge cases where visitors stand near a billing zone without queuing.
* **Test-Driven Development:** AI assisted in generating the `pytest` mock scenarios, specifically for simulating the `Camera Overlap Deduplication` anomalies and validating the 5-minute POS sliding window logic without needing massive test datasets.
* **FastAPI Routing:** AI was used to structure the FastAPI application into modular routers (`/metrics`, `/funnel`, `/anomalies`), ensuring the codebase remained clean and production-ready rather than a single monolithic file.
