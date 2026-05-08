# SentinelMesh 🛡️

> Autonomous multi-agent cybersecurity threat detection and response — powered by open-source LLMs on AMD ROCm.

Built for the **AMD Developer Hackathon** · Track 1: AI Agents & Agentic Workflows

---

## 📸 Platform Screenshots

> **sentinelmesh ss/WhatsApp Image 2026-05-08 at 12.28.03 PM.jpeg **
> *The central SOC platform tracking node telemetry and DeepSeek-R1 logic on AMD MI300X.*

> **[PLACEHOLDER_SCREENSHOT_2: Replace this line with a screenshot of the "Live Log Explorer" view]**
> *Live terminal output showing CrewAI orchestrated models parsing Kafka Event streams natively.*

> **[PLACEHOLDER_SCREENSHOT_3: Replace this line with a screenshot of the "Incidents" data table]**
> *Correlated kill chains and output analysis parsed safely into tactical alerts.*

---

## What is SentinelMesh?

SentinelMesh is a multi-agent AI system that autonomously monitors, classifies, correlates, and responds to cybersecurity threats in real time. Four specialised agents work in parallel — each with a focused role — orchestrated via CrewAI on AMD Instinct MI300X GPUs.

**Key advantage:** AMD MI300X's 192 GB HBM3 unified memory lets you run 70B-class models with full log history in-context. No chunking, no truncation, no missed correlations.

---

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    SentinelMesh Mesh                    │
│                                                         │
│  ┌──────────────┐      ┌────────────────────────────┐  │
│  │ LogHarvester │─────▶│    ThreatClassifier        │  │
│  │              │      │  DeepSeek-R1 / Llama 3.1   │  │
│  │ Ingests raw  │      │  70B on AMD MI300X         │  │
│  │ log streams  │      │  Scores & tags each event  │  │
│  └──────────────┘      └────────────┬───────────────┘  │
│                                     │                   │
│                                     ▼                   │
│                         ┌────────────────────────────┐  │
│                         │   CorrelationEngine        │  │
│                         │  Links events into         │  │
│                         │  kill chains (ATT&CK)      │  │
│                         └────────────┬───────────────┘  │
│                                      │                  │
│                                      ▼                  │
│                         ┌────────────────────────────┐  │
│                         │   IncidentWriter           │  │
│                         │  Auto-drafts IR reports    │  │
│                         │  + containment playbooks   │  │
│                         └────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | CrewAI + LangChain |
| LLM inference | DeepSeek-R1 70B, Llama 3.1 70B, Qwen2.5 |
| GPU compute | AMD Instinct MI300X via AMD Developer Cloud |
| GPU software | ROCm 6.x, PyTorch (ROCm build) |
| Log ingestion | Apache Kafka + custom parsers |
| Threat intel | MITRE ATT&CK STIX, VirusTotal API, AbuseIPDB |
| Backend | FastAPI + PostgreSQL + Redis |
| Frontend | React + Vite (SOC-Style multi-page dashboard) |

---

## Quickstart

### 1. Prerequisites
- AMD Developer Cloud account (developer.amd.com) or native ROCm 6.x GPU instance.
- Python 3.12+, Docker + Docker Compose, Node.js 18+

### 2. Clone & Setup Python
```bash
git clone https://github.com/evan-2005/sentinelmesh.git
cd sentinelmesh
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Configure API Keys
Edit `.env` and fill in your keys:
```env
# Crucial for AMD Hackathon
AMD_CLOUD_API_KEY=YOUR_AMD_KEY
VLLM_BASE_URL=https://api.amd.com/v1/inference
```

### 4. Start Infrastructure & APIs
```bash
sudo docker-compose up -d postgres redis kafka zookeeper
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 &
```

### 5. Launch the Dashboard
```bash
cd frontend && npm install
nohup npm run dev -- --host 0.0.0.0 &
```
*Visit the UI at `http://<SERVER_IP>:5173`*

### 6. Ignite the Mesh!
```bash
python -m orchestrator.crew
```

---

## Completed Hackathon Features
- [x] Wire real DeepSeek-R1 inference via AMD Developer Cloud endpoint
- [x] Integrate safe `LogHarvester` via Live Kafka syslog stream
- [x] ATT&CK STIX live DB lookup via STIX/TAXII
- [x] Full functional fallback to ensure LLMs correctly bypass LangChain Pydantic errors for custom endpoints
- [x] Multi-page hyper-dense SOC Dashboard React UI

---

## License

MIT — see [LICENSE](LICENSE)

---
*Built on AMD Developer Cloud · ROCm · CrewAI · DeepSeek · LangChain · MITRE ATT&CK*
