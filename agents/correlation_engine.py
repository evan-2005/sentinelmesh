"""
CorrelationEngine Agent
Links classified events into attack sequences (kill chains) by
building an event graph keyed on shared indicators (IP, user, host,
ATT&CK technique). Fires KillChainAlerts when 3+ stages are linked.
"""
import json
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Optional
from loguru import logger
from crewai import Agent
from langchain.tools import tool
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
KILL_CHAIN_STAGES = [
    "Reconnaissance",
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Credential Access",
    "Discovery",
    "Lateral Movement",
    "Collection",
    "Exfiltration",
    "Command and Control",
    "Impact",
]


def get_redis():
    import redis as r
    return r.from_url(REDIS_URL, decode_responses=True)


def store_event(event: dict) -> str:
    """Store event in Redis with a 24h TTL for the sliding window."""
    r = get_redis()
    event_id = event.get("id", f"evt-{datetime.now(timezone.utc).timestamp()}")
    key = f"sentinel:event:{event_id}"
    r.setex(key, int(timedelta(hours=24).total_seconds()), json.dumps(event))

    # Index by indicators for graph lookups
    classification = event.get("classification", {})
    tactic = classification.get("attack_tactic", "")
    for indicator_key, indicator_val in [
        ("src_ip", event.get("src_ip") or event.get("extensions", {}).get("src")),
        ("user", event.get("user")),
        ("host", event.get("host")),
        ("tactic", tactic),
    ]:
        if indicator_val:
            r.sadd(f"sentinel:index:{indicator_key}:{indicator_val}", event_id)
            r.expire(f"sentinel:index:{indicator_key}:{indicator_val}", 86400)

    return event_id


def find_related_events(event: dict) -> list[dict]:
    """Find events sharing indicators with the given event."""
    r = get_redis()
    related_ids = set()
    for indicator_key, indicator_val in [
        ("src_ip", event.get("src_ip")),
        ("user", event.get("user")),
        ("host", event.get("host")),
    ]:
        if indicator_val:
            ids = r.smembers(f"sentinel:index:{indicator_key}:{indicator_val}")
            related_ids.update(ids)

    related = []
    for eid in related_ids:
        raw = r.get(f"sentinel:event:{eid}")
        if raw:
            related.append(json.loads(raw))
    return related


def detect_kill_chain(events: list[dict]) -> Optional[dict]:
    """
    Check if a list of related events spans 3+ distinct ATT&CK tactics,
    indicating a multi-stage attack chain.
    """
    tactics_seen = set()
    for e in events:
        tactic = e.get("classification", {}).get("attack_tactic", "")
        if tactic:
            tactics_seen.add(tactic)

    ordered = [t for t in KILL_CHAIN_STAGES if t in tactics_seen]
    if len(ordered) >= 3:
        return {
            "type": "KillChainAlert",
            "stages_detected": ordered,
            "stage_count": len(ordered),
            "event_count": len(events),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    return None


@tool("correlate_event")
def correlate_event(classified_event_json: str) -> str:
    """
    Store a classified event and check if it forms part of a kill chain
    with previously seen events. Returns correlation result including
    any KillChainAlert if 3+ ATT&CK stages are linked.
    """
    try:
        event = json.loads(classified_event_json)
    except json.JSONDecodeError:
        return "ERROR: Invalid JSON input."

    event_id = store_event(event)
    related = find_related_events(event)
    kill_chain = detect_kill_chain(related)

    result = {
        "event_id": event_id,
        "related_events": len(related),
        "kill_chain_alert": kill_chain,
    }
    if kill_chain:
        logger.warning(f"KILL CHAIN DETECTED: {kill_chain['stages_detected']}")

    return json.dumps(result, indent=2)


@tool("get_active_kill_chains")
def get_active_kill_chains() -> str:
    """Return a summary of all active kill chains from the 24h sliding window."""
    r = get_redis()
    keys = r.keys("sentinel:event:*")
    events = [json.loads(r.get(k)) for k in keys if r.get(k)]

    # Group by source IP
    by_src: dict = defaultdict(list)
    for e in events:
        src = e.get("src_ip") or e.get("extensions", {}).get("src", "unknown")
        by_src[src].append(e)

    chains = []
    for src, evts in by_src.items():
        kc = detect_kill_chain(evts)
        if kc:
            chains.append({"source": src, **kc})

    return json.dumps({"active_kill_chains": chains, "total": len(chains)}, indent=2)


correlation_engine_agent = Agent(
    role="Correlation Engine",
    goal=(
        "Link classified security events into multi-stage attack sequences "
        "by finding shared indicators and matching MITRE ATT&CK kill chain patterns."
    ),
    backstory=(
        "You are an expert threat hunter who sees the connections others miss. "
        "You maintain a 24-hour view of all events and identify when isolated "
        "incidents are actually coordinated multi-stage attacks."
    ),
    tools=[correlate_event, get_active_kill_chains],
    verbose=True,
    allow_delegation=False,
)
