"""
IncidentWriter Agent
Triggered by KillChainAlerts or CRITICAL events. Drafts structured
IR reports (Markdown) and step-by-step containment playbooks using
the LLM, then stores them in PostgreSQL.
"""
import json
import os
from datetime import datetime, timezone
from crewai import Agent
from langchain.tools import tool
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8080/v1")
VLLM_MODEL = os.getenv("VLLM_MODEL", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B")

IR_SYSTEM_PROMPT = """You are a senior cybersecurity incident responder writing formal IR reports.
Given a kill chain alert and its associated events, produce a structured Markdown report with:

## Executive Summary
One paragraph for non-technical leadership.

## Incident Timeline
Chronological list of events with timestamps.

## Attack Chain Analysis
Map each stage to MITRE ATT&CK tactics and techniques.

## Affected Assets
List all impacted hosts, users, and systems.

## Evidence Summary
Key indicators of compromise (IOCs): IPs, hashes, domains, usernames.

## Containment Playbook
Step-by-step numbered instructions for immediate containment.

## Eradication & Recovery Steps
Steps to remove the threat and restore normal operations.

## Recommendations
3-5 strategic recommendations to prevent recurrence.

Use professional, precise language. Be specific — include actual IPs, usernames, and technique IDs from the data."""


def get_llm():
    return ChatOpenAI(
        base_url=VLLM_BASE_URL,
        api_key=os.getenv("AMD_CLOUD_API_KEY", "EMPTY"),
        model=VLLM_MODEL,
        temperature=0.2,
        max_tokens=2048,
    )


def next_ir_number() -> str:
    """Generate a sequential IR report number."""
    ts = datetime.now(timezone.utc)
    return f"IR-{ts.year}{ts.month:02d}{ts.day:02d}-{ts.hour:02d}{ts.minute:02d}"


@tool("draft_ir_report")
def draft_ir_report(kill_chain_json: str) -> str:
    """
    Given a JSON string containing a KillChainAlert and its associated events,
    draft a full Incident Response report in Markdown format and return it.
    """
    try:
        data = json.loads(kill_chain_json)
    except json.JSONDecodeError:
        return "ERROR: Invalid JSON input."

    ir_id = next_ir_number()
    prompt = (
        f"Incident ID: {ir_id}\n"
        f"Generated at: {datetime.now(timezone.utc).isoformat()}\n\n"
        f"Kill Chain Data:\n{json.dumps(data, indent=2)}"
    )

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=IR_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    report = f"# Incident Report {ir_id}\n\n{response.content}"
    logger.info(f"Drafted IR report {ir_id}")
    return report


@tool("draft_containment_playbook")
def draft_containment_playbook(event_summary: str) -> str:
    """
    Given a brief summary of a threat event, generate a step-by-step
    containment and remediation playbook in Markdown.
    """
    llm = get_llm()
    system = (
        "You are a cybersecurity incident responder. "
        "Write a concise, numbered containment playbook for the described threat. "
        "Include: immediate isolation steps, evidence preservation, credential resets, "
        "and validation checks. Be specific and actionable."
    )
    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=f"Threat summary:\n{event_summary}"),
    ])
    return response.content


@tool("save_report_to_db")
def save_report_to_db(report_markdown: str) -> str:
    """
    Save a completed IR report to PostgreSQL.
    Returns the saved report ID.
    """
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv("POSTGRES_URL"))
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ir_reports (content, created_at) VALUES (%s, %s) RETURNING id",
            (report_markdown, datetime.now(timezone.utc))
        )
        report_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return f"Report saved with ID: {report_id}"
    except Exception as e:
        return f"DB save failed (report still returned above): {e}"


incident_writer_agent = Agent(
    role="Incident Writer",
    goal=(
        "Automatically draft complete Incident Response reports and containment "
        "playbooks for every detected kill chain or CRITICAL event."
    ),
    backstory=(
        "You are a senior IR analyst who writes clear, actionable reports under "
        "pressure. Your reports bridge the gap between technical findings and "
        "executive decision-making, and your playbooks get threats contained fast."
    ),
    tools=[draft_ir_report, draft_containment_playbook, save_report_to_db],
    verbose=True,
    allow_delegation=False,
)
