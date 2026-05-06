"""
LogHarvester Agent
Ingests raw log streams (syslog, CEF, JSON) and normalises them
into a common ECS-compatible schema, then publishes to Kafka.
"""
import json
import re
import asyncio
from datetime import datetime, timezone
from typing import Optional
from loguru import logger
from crewai import Agent
from langchain.tools import tool
import os

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_RAW = os.getenv("KAFKA_TOPIC_RAW", "sentinel.events.raw")


def get_producer():
    from kafka import KafkaProducer
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def normalise_syslog(raw: str) -> Optional[dict]:
    pattern = r"<(\d+)>(\w+ +\d+ \d+:\d+:\d+) (\S+) (\S+): (.+)"
    m = re.match(pattern, raw.strip())
    if not m:
        return None
    priority, timestamp, host, process, message = m.groups()
    return {
        "source_type": "syslog",
        "timestamp": timestamp,
        "host": host,
        "process": process,
        "message": message,
        "raw_severity": int(priority) & 0x07,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }


def normalise_cef(raw: str) -> Optional[dict]:
    if not raw.startswith("CEF:"):
        return None
    try:
        parts = raw.split("|")
        ext_str = parts[-1] if len(parts) > 7 else ""
        extensions = {}
        for kv in ext_str.strip().split(" "):
            if "=" in kv:
                k, v = kv.split("=", 1)
                extensions[k] = v
        return {
            "source_type": "cef",
            "vendor": parts[1],
            "product": parts[2],
            "name": parts[5],
            "severity": parts[6],
            "extensions": extensions,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        return None


def normalise_json_log(raw: str) -> Optional[dict]:
    try:
        data = json.loads(raw)
        data.update({"source_type": "json", "ingested_at": datetime.now(timezone.utc).isoformat()})
        return data
    except json.JSONDecodeError:
        return None


def normalise(raw: str) -> Optional[dict]:
    if raw.startswith("CEF:"):
        return normalise_cef(raw)
    if raw.strip().startswith("{"):
        return normalise_json_log(raw)
    return normalise_syslog(raw)


@tool("parse_and_publish_log")
def parse_and_publish_log(raw_log: str) -> str:
    """Parse a raw log line and publish it to Kafka for threat classification."""
    event = normalise(raw_log)
    if not event:
        return f"ERROR: Could not parse: {raw_log[:80]}"
    try:
        get_producer().send(TOPIC_RAW, event)
        return json.dumps(event, indent=2)
    except Exception as e:
        return f"ERROR publishing to Kafka: {e}"


@tool("batch_parse_logs")
def batch_parse_logs(log_lines: str) -> str:
    """Parse and publish multiple newline-separated log lines."""
    lines = [l for l in log_lines.strip().split("\n") if l.strip()]
    ok, fail = 0, 0
    producer = get_producer()
    for line in lines:
        event = normalise(line)
        if event:
            producer.send(TOPIC_RAW, event)
            ok += 1
        else:
            fail += 1
    producer.flush()
    return f"Parsed {ok} events OK, {fail} failed. Published to {TOPIC_RAW}."


log_harvester_agent = Agent(
    role="Log Harvester",
    goal="Ingest, parse, and normalise all incoming log streams into structured security events.",
    backstory=(
        "You are a log parsing specialist with deep knowledge of syslog, CEF, "
        "and JSON formats. You output clean, structured events ready for AI analysis."
    ),
    tools=[parse_and_publish_log, batch_parse_logs],
    verbose=True,
    allow_delegation=False,
)
