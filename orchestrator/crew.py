"""
SentinelMesh Crew
Wires all four agents together using CrewAI. The crew runs as a
continuous pipeline: ingest -> classify -> correlate -> report.
"""
import json
import os

# Polyfill OpenAI requirements for CrewAI to use AMD vLLM directly
os.environ["OPENAI_API_KEY"] = "dummy"
os.environ["OPENAI_API_BASE"] = os.environ.get("VLLM_BASE_URL", "http://localhost:8080/v1")
from crewai import Crew, Task
from agents.log_harvester import log_harvester_agent
from agents.threat_classifier import threat_classifier_agent
from agents.correlation_engine import correlation_engine_agent
from agents.incident_writer import incident_writer_agent
from loguru import logger


def build_pipeline_tasks(raw_logs: list[str]) -> list[Task]:
    """Build the four-stage task pipeline for a batch of raw logs."""
    log_blob = "\n".join(raw_logs)

    ingest_task = Task(
        description=(
            f"Parse and normalise the following raw log lines, publishing each "
            f"to the Kafka pipeline. Return a JSON array of normalised events.\n\n"
            f"Raw logs:\n{log_blob}"
        ),
        agent=log_harvester_agent,
        expected_output="JSON array of normalised security events.",
    )

    classify_task = Task(
        description=(
            "Take the normalised events from the previous step and classify each one "
            "using the DeepSeek-R1 threat classifier. Assign severity, MITRE ATT&CK "
            "technique, and confidence score. Return a JSON array of classified events."
        ),
        agent=threat_classifier_agent,
        expected_output="JSON array of classified events with severity and ATT&CK mapping.",
        context=[ingest_task],
    )

    correlate_task = Task(
        description=(
            "Correlate the classified events. Store each in the sliding window and "
            "check for kill chain patterns across shared indicators. Report any "
            "KillChainAlerts detected, including which stages were observed."
        ),
        agent=correlation_engine_agent,
        expected_output="Correlation report including any KillChainAlerts.",
        context=[classify_task],
    )

    report_task = Task(
        description=(
            "If any KillChainAlerts were detected in the previous step, draft a full "
            "Incident Response report and containment playbook. If no kill chain was "
            "detected but CRITICAL events exist, draft a containment playbook for those. "
            "Return the completed report in Markdown."
        ),
        agent=incident_writer_agent,
        expected_output="Completed IR report and containment playbook in Markdown.",
        context=[correlate_task],
    )

    return [ingest_task, classify_task, correlate_task, report_task]


def run_pipeline(raw_logs: list[str]) -> str:
    """Execute the full SentinelMesh pipeline on a batch of raw log lines."""
    tasks = build_pipeline_tasks(raw_logs)
    crew = Crew(
        agents=[
            log_harvester_agent,
            threat_classifier_agent,
            correlation_engine_agent,
            incident_writer_agent,
        ],
        tasks=tasks,
        verbose=True,
    )
    result = crew.kickoff()
    return result


if __name__ == "__main__":
    # Smoke test with sample log lines
    sample_logs = [
        '<34>Oct 11 22:14:15 prod-db-03 sudo: svc_backup : command not allowed ; TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/bash',
        'CEF:0|Linux|auditd|1.0|2|Privilege escalation attempt|10|src=10.0.0.5 dst=prod-db-03 duser=root',
        '{"timestamp":"2024-01-15T02:14:00Z","host":"api-gw-01","event":"failed_login","user":"admin","src_ip":"213.184.248.10","count":428}',
        '{"timestamp":"2024-01-15T02:15:00Z","host":"prod-db-03","event":"lateral_movement","src_ip":"192.168.4.12","protocol":"SMB"}',
    ]
    logger.info("Starting SentinelMesh pipeline...")
    result = run_pipeline(sample_logs)
    print("\n" + "="*60)
    print("PIPELINE RESULT:")
    print("="*60)
    print(result)
