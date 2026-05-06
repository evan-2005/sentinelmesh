# SentinelMesh 🛡️

> Autonomous multi-agent cybersecurity threat detection and response — powered by open-source LLMs on AMD ROCm.

Built for the **AMD Developer Hackathon** · Track 1: AI Agents & Agentic Workflows

---

## What is SentinelMesh?

SentinelMesh is a multi-agent AI system that autonomously monitors, classifies, correlates, and responds to cybersecurity threats in real time. Four specialised agents work in parallel — each with a focused role — orchestrated via CrewAI on AMD Instinct MI300X GPUs.

**Key advantage:** AMD MI300X's 192 GB HBM3 unified memory lets you run 70B-class models with full log history in-context. No chunking, no truncation, no missed correlations.

---

## Architecture

```
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
| Serving | vLLM (ROCm fork) |
| Log ingestion | Apache Kafka + custom parsers |
| Threat intel | MITRE ATT&CK STIX, VirusTotal API, AbuseIPDB |
| Backend | FastAPI + PostgreSQL + Redis |
| Frontend | React |

---

## Project Structure

```
sentinelmesh/
├── agents/
│   ├── log_harvester.py        # Log ingestion & normalisation
│   ├── threat_classifier.py   # LLM-based threat scoring
│   ├── correlation_engine.py  # Kill chain correlation
│   └── incident_writer.py     # IR report generation
├── orchestrator/
│   ├── crew.py                # CrewAI crew definition
│   └── tools/
│       ├── virustotal.py      # VirusTotal API tool
│       ├── abuseipdb.py       # IP reputation tool
│       └── attack_lookup.py   # MITRE ATT&CK STIX tool
├── inference/
│   ├── rocm_client.py         # AMD Developer Cloud client
│   └── vllm_server.py         # vLLM config for MI300X
├── api/
│   ├── main.py                # FastAPI app entry point
│   ├── models.py              # Pydantic schemas
│   └── routes/
│       ├── events.py          # Threat event endpoints
│       └── agents.py          # Agent status endpoints
├── frontend/src/              # React dashboard
├── data/sample_logs/          # Sample syslog, CEF, EVTX logs
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quickstart

### 1. Prerequisites
- AMD Developer Cloud account (developer.amd.com)
- ROCm 6.x or AMD Developer Cloud environment
- Python 3.11+, Docker + Docker Compose, Node.js 18+

### 2. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/sentinelmesh.git
cd sentinelmesh
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Start infrastructure
```bash
docker-compose up -d postgres redis kafka zookeeper
```

### 5. Launch the agent mesh
```bash
python -m orchestrator.crew
```

### 6. Start API + frontend
```bash
uvicorn api.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

Dashboard → `http://localhost:3000` · API docs → `http://localhost:8000/docs`

---

## Refinement Roadmap
- [ ] Wire real DeepSeek-R1 inference via AMD Developer Cloud endpoint
- [ ] Connect LogHarvester to live Kafka syslog stream
- [ ] ATT&CK STIX graph integration in CorrelationEngine
- [ ] Neo4j persistence for the event correlation graph
- [ ] Hugging Face Space deployment for hackathon submission
- [ ] 2x Build in Public posts tagging @AIatAMD + @lablab

---

## License

MIT — see [LICENSE](LICENSE)

---
*Built on AMD Developer Cloud · ROCm · CrewAI · DeepSeek · LangChain · MITRE ATT&CK*
