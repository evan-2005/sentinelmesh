"""VirusTotal API tool for IOC enrichment."""
import os
import requests
from langchain.tools import tool

VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
VT_BASE = "https://www.virustotal.com/api/v3"


def _vt_get(endpoint: str) -> dict:
    headers = {"x-apikey": VT_API_KEY}
    r = requests.get(f"{VT_BASE}/{endpoint}", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


@tool("virustotal_ip_lookup")
def virustotal_ip_lookup(ip_address: str) -> str:
    """Look up an IP address on VirusTotal and return reputation data."""
    if not VT_API_KEY:
        return "ERROR: VIRUSTOTAL_API_KEY not set."
    try:
        data = _vt_get(f"ip_addresses/{ip_address}")
        attrs = data.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        return (
            f"IP: {ip_address} | "
            f"Malicious: {stats.get('malicious', 0)} | "
            f"Suspicious: {stats.get('suspicious', 0)} | "
            f"Country: {attrs.get('country', 'unknown')} | "
            f"ASN: {attrs.get('asn', 'unknown')}"
        )
    except Exception as e:
        return f"ERROR: VT lookup failed: {e}"


@tool("virustotal_hash_lookup")
def virustotal_hash_lookup(file_hash: str) -> str:
    """Look up a file hash (MD5/SHA1/SHA256) on VirusTotal."""
    if not VT_API_KEY:
        return "ERROR: VIRUSTOTAL_API_KEY not set."
    try:
        data = _vt_get(f"files/{file_hash}")
        attrs = data.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        return (
            f"Hash: {file_hash} | "
            f"Malicious: {stats.get('malicious', 0)} | "
            f"Name: {attrs.get('meaningful_name', 'unknown')} | "
            f"Type: {attrs.get('type_description', 'unknown')}"
        )
    except Exception as e:
        return f"ERROR: VT lookup failed: {e}"
