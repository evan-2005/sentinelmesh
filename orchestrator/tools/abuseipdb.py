"""AbuseIPDB reputation lookup tool."""
import os
import requests
from langchain.tools import tool

ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_API_KEY", "")
ABUSEIPDB_BASE = "https://api.abuseipdb.com/api/v2"


@tool("abuseipdb_check")
def abuseipdb_check(ip_address: str) -> str:
    """
    Check an IP address against AbuseIPDB.
    Returns abuse confidence score, ISP, and usage type.
    """
    if not ABUSEIPDB_KEY:
        return "ERROR: ABUSEIPDB_API_KEY not set."
    try:
        headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
        params = {"ipAddress": ip_address, "maxAgeInDays": 90}
        r = requests.get(f"{ABUSEIPDB_BASE}/check", headers=headers, params=params, timeout=10)
        r.raise_for_status()
        d = r.json().get("data", {})
        return (
            f"IP: {ip_address} | "
            f"Abuse confidence: {d.get('abuseConfidenceScore', 0)}% | "
            f"ISP: {d.get('isp', 'unknown')} | "
            f"Usage type: {d.get('usageType', 'unknown')} | "
            f"Reports: {d.get('totalReports', 0)} in 90d"
        )
    except Exception as e:
        return f"ERROR: AbuseIPDB lookup failed: {e}"
