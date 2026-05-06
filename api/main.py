"""
SentinelMesh FastAPI Application
Provides REST endpoints for the dashboard to query threat events,
agent status, and IR reports. Also accepts log ingest requests.
"""
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.models import IngestRequest, IngestResponse, AgentStatus
from loguru import logger

app = FastAPI(
    title="SentinelMesh API",
    description="Autonomous multi-agent cybersecurity threat detection",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_logs(request: IngestRequest):
    """Accept a batch of raw log lines and push them into the pipeline."""
    job_id = str(uuid.uuid4())
    logger.info(f"Received {len(request.logs)} log lines, job {job_id}")
    # TODO: publish to Kafka TOPIC_RAW for async pipeline processing
    return IngestResponse(accepted=len(request.logs), job_id=job_id)


@app.get("/api/agents", response_model=list[AgentStatus])
async def get_agents():
    """Return current status of all four agents."""
    # TODO: read real agent state from Redis
    return [
        AgentStatus(name="LogHarvester", status="busy", current_task="parsing 12 log streams", events_processed=14823, load_pct=78),
        AgentStatus(name="ThreatClassifier", status="busy", current_task="running DeepSeek-R1", events_processed=14750, load_pct=91),
        AgentStatus(name="CorrelationEngine", status="active", current_task="4 active kill chains", events_processed=14750, load_pct=55),
        AgentStatus(name="IncidentWriter", status="active", current_task="drafting IR-20240115-0214", events_processed=12, load_pct=40),
    ]


# Import and include route modules
from api.routes import events, agents as agents_router
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(agents_router.router, prefix="/api/agents-detail", tags=["agents"])
