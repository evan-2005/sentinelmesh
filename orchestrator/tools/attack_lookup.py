"""MITRE ATT&CK STIX lookup tool."""
from langchain.tools import tool

# Lightweight static map of common techniques.
# TODO: replace with full STIX dataset query via taxii2-client.
ATTACK_MAP = {
    "T1557": {"name": "Adversary-in-the-Middle", "tactic": "Credential Access", "url": "https://attack.mitre.org/techniques/T1557/"},
    "T1048": {"name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "url": "https://attack.mitre.org/techniques/T1048/"},
    "T1548": {"name": "Abuse Elevation Control Mechanism", "tactic": "Privilege Escalation", "url": "https://attack.mitre.org/techniques/T1548/"},
    "T1078": {"name": "Valid Accounts", "tactic": "Initial Access", "url": "https://attack.mitre.org/techniques/T1078/"},
    "T1595": {"name": "Active Scanning", "tactic": "Reconnaissance", "url": "https://attack.mitre.org/techniques/T1595/"},
    "T1110": {"name": "Brute Force", "tactic": "Credential Access", "url": "https://attack.mitre.org/techniques/T1110/"},
    "T1021": {"name": "Remote Services", "tactic": "Lateral Movement", "url": "https://attack.mitre.org/techniques/T1021/"},
}


@tool("attack_technique_lookup")
def attack_technique_lookup(technique_id: str) -> str:
    """
    Look up a MITRE ATT&CK technique by ID (e.g. T1557).
    Returns the technique name, tactic, and ATT&CK URL.
    """
    info = ATTACK_MAP.get(technique_id.upper())
    if not info:
        return f"Technique {technique_id} not found in local map. Check https://attack.mitre.org/techniques/{technique_id}/"
    return (
        f"Technique: {technique_id} — {info['name']} | "
        f"Tactic: {info['tactic']} | "
        f"Reference: {info['url']}"
    )


@tool("search_attack_by_tactic")
def search_attack_by_tactic(tactic_name: str) -> str:
    """Return all known techniques for a given ATT&CK tactic name."""
    matches = {k: v for k, v in ATTACK_MAP.items() if tactic_name.lower() in v["tactic"].lower()}
    if not matches:
        return f"No techniques found for tactic: {tactic_name}"
    lines = [f"{k}: {v['name']}" for k, v in matches.items()]
    return "\n".join(lines)
