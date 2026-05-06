"""MITRE ATT&CK STIX lookup tool."""
from langchain.tools import tool
from stix2 import TAXIICollectionSource, Filter
from taxii2client.v20 import Collection

# Connect to MITRE Enterprise ATT&CK collection
collection = Collection("https://cti-taxii.mitre.org/stix/collections/95ecc380-afe9-11e4-9b6c-751b66dd541e/")
src = TAXIICollectionSource(collection)

@tool("attack_technique_lookup")
def attack_technique_lookup(technique_id: str) -> str:
    """
    Look up a MITRE ATT&CK technique by ID (e.g. T1557) via a STIX TAXII feed.
    """
    try:
        filt = [Filter('type', '=', 'attack-pattern'), Filter('external_references.external_id', '=', technique_id.upper())]
        results = src.query(filt)
        if not results:
            return f"Technique {technique_id} not found in STIX dataset. Check https://attack.mitre.org/techniques/{technique_id}/"
            
        tech = results[0]
        tactics = [phase.phase_name for phase in tech.get('kill_chain_phases', [])]
        tactic_str = ", ".join(tactics) if tactics else "Unknown"
        ref_url = tech.get("external_references", [{}])[0].get("url", f"https://attack.mitre.org/techniques/{technique_id.upper()}/")
        
        return (
            f"Technique: {technique_id.upper()} — {tech.name} | "
            f"Tactic: {tactic_str} | "
            f"Reference: {ref_url}"
        )
    except Exception as e:
        return f"Error querying STIX feed: {e}"

@tool("search_attack_by_tactic")
def search_attack_by_tactic(tactic_name: str) -> str:
    """Return all known techniques for a given ATT&CK tactic name, using STIX TAXII feed."""
    try:
        filt = [Filter('type', '=', 'attack-pattern'), Filter('kill_chain_phases.phase_name', '=', tactic_name.lower().replace(" ", "-"))]
        results = src.query(filt)
        if not results:
            return f"No techniques found for tactic: {tactic_name}"
            
        lines = []
        for tech in results:
            ext_id = "Unknown"
            for ref in tech.get('external_references', []):
                if ref.source_name == 'mitre-attack':
                    ext_id = ref.external_id
                    break
            lines.append(f"{ext_id}: {tech.name}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error querying STIX feed: {e}"
