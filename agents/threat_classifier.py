"""
ThreatClassifier Agent
Uses DeepSeek-R1 (via AMD Developer Cloud / vLLM on ROCm) to score
each normalised event for severity, MITRE ATT&CK technique, and
confidence. Publishes classified events to Kafka.
"""
import json
import os
from loguru import logger
from crewai import Agent
from langchain.tools import tool
from inference.rocm_client import chat_completion_sync

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8080/v1")
VLLM_MODEL = os.getenv("VLLM_MODEL", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B")
TOPIC_CLASSIFIED = os.getenv("KAFKA_TOPIC_CLASSIFIED", "sentinel.events.classified")

CLASSIFIER_SYSTEM_PROMPT = """You are a cybersecurity threat classification expert.
Given a normalised security event, respond ONLY with a JSON object containing:
- severity: one of CRITICAL, HIGH, MEDIUM, LOW, INFO
- attack_tactic: MITRE ATT&CK tactic name (e.g. "Lateral Movement")
- attack_technique_id: MITRE ATT&CK technique ID (e.g. "T1557")
- attack_technique_name: human-readable technique name
- confidence: integer 0-100
- reasoning: 2-3 sentence explanation
- recommended_action: immediate action to take

Respond ONLY with valid JSON. No preamble, no markdown fences."""


def classify_event(event: dict) -> dict:
    """Run the LLM classifier on a single event dict using ROCm client."""
    prompt = f"Classify this security event:\n\n{json.dumps(event, indent=2)}"
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response_content = chat_completion_sync(
            messages=messages,
            model=VLLM_MODEL,
            temperature=0.1,
            max_tokens=512
        )
        # Parse output ensuring no markdown fences
        clean_content = response_content.strip()
        if clean_content.startswith("```json"):
            clean_content = clean_content[7:]
        if clean_content.startswith("```"):
            clean_content = clean_content[3:]
        if clean_content.endswith("```"):
            clean_content = clean_content[:-3]
            
        classification = json.loads(clean_content.strip())
    except Exception as e:
        logger.warning(f"Classification failed: {e}")
        classification = {
            "severity": "UNKNOWN",
            "confidence": 0,
            "reasoning": "LLM returned non-JSON response or request failed.",
            "raw_response": str(e),
        }
    return {**event, "classification": classification}


@tool("classify_security_event")
def classify_security_event(event_json: str) -> str:
    """
    Given a JSON string of a normalised security event, run the
    DeepSeek-R1 threat classifier and return a classified event JSON.
    Publishes the result to Kafka automatically.
    """
    try:
        event = json.loads(event_json)
    except json.JSONDecodeError:
        return "ERROR: Invalid JSON input."

    classified = classify_event(event)

    # Publish to classified topic
    try:
        from kafka import KafkaProducer
        import os
        producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        producer.send(TOPIC_CLASSIFIED, classified)
        producer.flush()
    except Exception as e:
        logger.warning(f"Could not publish to Kafka: {e}")

    return json.dumps(classified, indent=2)


@tool("bulk_classify_events")
def bulk_classify_events(events_json: str) -> str:
    """
    Given a JSON array of normalised events, classify each one and
    return a summary with severity counts.
    """
    try:
        events = json.loads(events_json)
    except json.JSONDecodeError:
        return "ERROR: Expected a JSON array of events."

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0, "UNKNOWN": 0}
    results = []
    for event in events:
        classified = classify_event(event)
        sev = classified.get("classification", {}).get("severity", "UNKNOWN")
        counts[sev] = counts.get(sev, 0) + 1
        results.append(classified)

    return json.dumps({"summary": counts, "events": results}, indent=2)


threat_classifier_agent = Agent(
    role="Threat Classifier",
    goal=(
        "Use DeepSeek-R1 running on AMD MI300X to classify each security event "
        "with a severity rating, MITRE ATT&CK mapping, and confidence score."
    ),
    backstory=(
        "You are an AI-powered threat analyst. You leverage large language models "
        "running on AMD GPUs to analyse security events faster and more accurately "
        "than any human analyst, at massive scale."
    ),
    tools=[classify_security_event, bulk_classify_events],
    verbose=True,
    allow_delegation=False,
)
