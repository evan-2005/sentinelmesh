"""Pydantic schemas for the SentinelMesh API."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class Classification(BaseModel):
    severity: str
    attack_tactic: Optional[str] = None
    attack_technique_id: Optional[str] = None
    attack_technique_name: Optional[str] = None
    confidence: int
    reasoning: str
    recommended_action: Optional[str] = None


class ThreatEvent(BaseModel):
    id: str
    source_type: str
    timestamp: Optional[str] = None
    host: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    message: Optional[str] = None
    classification: Optional[Classification] = None
    ingested_at: datetime
    extensions: Optional[dict] = None


class KillChainAlert(BaseModel):
    type: str = "KillChainAlert"
    stages_detected: list[str]
    stage_count: int
    event_count: int
    generated_at: datetime


class IRReport(BaseModel):
    id: Optional[int] = None
    content: str
    created_at: Optional[datetime] = None


class AgentStatus(BaseModel):
    name: str
    status: str  # active | busy | idle | error
    current_task: Optional[str] = None
    events_processed: int
    load_pct: int


class IngestRequest(BaseModel):
    logs: list[str]


class IngestResponse(BaseModel):
    accepted: int
    job_id: str
