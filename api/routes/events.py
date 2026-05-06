"""Threat event endpoints."""
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/")
async def list_events(
    severity: Optional[str] = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"),
    limit: int = Query(50, le=500),
):
    """List recent threat events, optionally filtered by severity."""
    # TODO: query from PostgreSQL
    return {"events": [], "total": 0, "filters": {"severity": severity, "limit": limit}}


@router.get("/{event_id}")
async def get_event(event_id: str):
    """Get a single threat event by ID."""
    # TODO: query from PostgreSQL
    return {"event_id": event_id, "detail": "not implemented yet"}


@router.get("/kill-chains/active")
async def active_kill_chains():
    """Return all active kill chain alerts from the 24h sliding window."""
    # TODO: query from Redis via CorrelationEngine
    return {"kill_chains": [], "total": 0}
