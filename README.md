# AuraTrack - Retail Intelligence API

AuraTrack is an end-to-end computer vision and API pipeline that tracks retail visitors, measures zone dwell times, and correlates billing queue events with legacy point-of-sale data to calculate real-time conversion rates.

## Directory Structure & File Placement
To run this project correctly, ensure your files are placed in the following exact directory structure:

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

## Setup & Execution in just 5 Commands

To satisfy the production readiness requirements, the system is fully containerized. Ensure Docker and `uv` are installed on your machine, if not then simply use `pip` then execute these exact commands in order:

```bash
# 1. Clone the repository and enter the directory
git clone https://github.com/dev-satyamjha/AuraTrack && cd AuraTrack

# 2. Launch the FastAPI backend in the background via Docker
docker compose up --build -d

# 3. Create a virtual environment and install dependencies instantly via pyproject.toml
uv sync

# 4. Verify the API logic using the automated Pytest suite
uv run pytest tests/

# 5. Execute the batch processing pipeline to process all cameras
uv run bash pipeline/run.sh

```
👉 **Sample Output:** You can view the generated AI data payload in `pipeline/sample_output.json`.

---

# System Verification Steps

---

## 1. API Documentation & Idempotency

Once the API is live. You can view the interactive Swagger dashboard at:

👉 `http://localhost:8000/docs`

The `/events/ingest` endpoint is built with strict idempotency (using hashed `id_token` and `event_time` tracking) to ensure that network retries do not inflate store traffic metrics.

---

## 2. Live Dashboard (Part E Requirement)

To view the live terminal dashboard and prove the real-time socket connection between the vision pipeline and the API:

1. Open a new terminal window at the project root.
2. Run the dashboard:
   ```bash
   python dashboard.py
   ```
   > **Note:** You can pass a store ID dynamically, e.g., `python dashboard.py ST1009`. It defaults to `ST1008`.
3. As the videos process during Step 5, you will watch the Terminal UI (TUI) automatically update the metrics and queue depths in real-time.

---

## 3. POS Correlation (Funnel Analytics)

Once the pipeline finishes running against the video clips, query the `/funnel/conversion/ST1008` endpoint in your browser or via the Swagger UI.

The API will evaluate a **5-minute sliding window** from the time a visitor abandoned or completed the billing queue and match it against the legacy `pos_transactions.csv` file to output the final **Conversion Rate**.

---
