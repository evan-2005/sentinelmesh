"""Agent status and control endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def agent_status():
    """Detailed agent status including task queue depth."""
    # TODO: read from Redis agent state keys
    return {"agents": {}}


@router.post("/{agent_name}/restart")
async def restart_agent(agent_name: str):
    """Restart a specific agent (admin only in production)."""
    # TODO: implement agent lifecycle control
    return {"status": "restarted", "agent": agent_name}
