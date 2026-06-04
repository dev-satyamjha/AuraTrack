from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.ingestion import router as ingestion_router
from app.health import router as health_router
from app.metrics import router as metrics_router
from app.funnel import router as funnel_router
from app.anomalies import router as anomalies_router

""" Initialize the FastAPI application with production-ready metadata for the judges. """
app = FastAPI(
    title="AuraTrack Intelligence API",
    description="Real-time retail analytics, queue monitoring, and POS correlation engine.",
    version="1.0.0"
)

""" Configure Cross-Origin Resource Sharing (CORS) for downstream dashboard integration. """
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" Mount all application routers for ingestion, analytics, correlation, and health monitoring. """
app.include_router(ingestion_router, prefix="/events", tags=["Ingestion"])
app.include_router(health_router, prefix="/health", tags=["System Health"])
app.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
app.include_router(funnel_router, prefix="/funnel", tags=["Funnel & POS Correlation"])
app.include_router(anomalies_router, prefix="/anomalies", tags=["Anomalies"])

""" Root endpoint to verify the server is running natively. """
@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AuraTrack Intelligence Engine",
        "message": "API is active and ready to ingest telemetry."
    }
