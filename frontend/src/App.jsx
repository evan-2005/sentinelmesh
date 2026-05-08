import React, { useState, useEffect, useRef } from "react";
import "./App.css";

const API = `http://${window.location.hostname}:8000/api`;

// --- SUB-COMPONENTS --- //

const PageAgents = ({ agents }) => {
  return (
    <>
      <div className="section-header">
        <h3>Active Mesh Agents</h3>
        {agents.length > 0 && <span className="agent-count">({agents.length} nodes running)</span>}
      </div>

      <div className="info-ribbon">
        <div className="ribbon-card">
          <span className="ribbon-label">TOTAL SYS INGEST</span>
          <span className="ribbon-value">2.4 TB/s</span>
        </div>
        <div className="ribbon-card">
          <span className="ribbon-label">ANOMALIES DETECTED</span>
          <span className="ribbon-value pending">142</span>
        </div>
        <div className="ribbon-card">
          <span className="ribbon-label">MITIGATED THREATS</span>
          <span className="ribbon-value success">89</span>
        </div>
        <div className="ribbon-card">
          <span className="ribbon-label">ACTIVE PLAYBOOKS</span>
          <span className="ribbon-value">4</span>
        </div>
      </div>

      <div className="telemetry-grid">
        {agents.length === 0 && <div className="system-loading">[SYSTEM] Waiting for telemetry link...</div>}
        {agents.map((a) => (
          <div key={a.name} className={`node-panel ${a.status}`}>
            <div className="panel-header">
              <div className="node-id">
                <span className="brackets">[</span>{a.name.toUpperCase()}<span className="brackets">]</span>
              </div>
              <div className={`status-badge ${a.status}`}>{a.status.toUpperCase()}</div>
            </div>

            <div className="panel-body">
              <div className="data-row">
                <span className="data-label">COMPUTE LOAD</span>
                <div className="data-progress-wrapper">
                  <div className="data-progress" style={{ width: `${a.load_pct}%` }}></div>
                </div>
                <span className="data-value">{a.load_pct}%</span>
              </div>

              <div className="data-row">
                <span className="data-label">EVENTS PROC</span>
                <span className="data-value emp">{a.events_processed.toLocaleString()}</span>
              </div>

              <div className="task-box">
                <div className="task-label">CURRENT INSTRUCTION</div>
                <div className="task-cmd">&gt; {a.current_task}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
};

const PageIncidents = () => {
  const incidents = [
    { id: "INC-990", time: "2026-05-08 02:14:00", severity: "CRITICAL", source: "192.168.4.12", desc: "Lateral movement via SMB" },
    { id: "INC-989", time: "2026-05-08 02:12:35", severity: "HIGH", source: "10.0.0.5", desc: "Privilege escalation attempt (root)" },
    { id: "INC-988", time: "2026-05-08 02:08:11", severity: "MEDIUM", source: "213.184.248.10", desc: "Failed login anomalous spike" },
    { id: "INC-987", time: "2026-05-08 01:54:20", severity: "LOW", source: "10.20.5.55", desc: "Unusual outbound connection" },
    { id: "INC-986", time: "2026-05-08 01:10:05", severity: "CRITICAL", source: "10.128.0.2", desc: "Data exfiltration pattern detected" },
  ];

  return (
    <>
      <div className="section-header">
        <h3>Incident Tracker</h3>
      </div>
      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>TIMESTAMP (UTC)</th>
              <th>SEVERITY</th>
              <th>SOURCE</th>
              <th>THREAT DESCRIPTION</th>
              <th>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map(inc => (
              <tr key={inc.id}>
                <td>{inc.id}</td>
                <td>{inc.time}</td>
                <td><span className={`sev-badge ${inc.severity.toLowerCase()}`}>{inc.severity}</span></td>
                <td className="ip-text">{inc.source}</td>
                <td>{inc.desc}</td>
                <td><button className="btn-action">INVESTIGATE</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
};

const PageLogs = () => {
  const [lines, setLines] = useState(["> SYSTEM TTY/1 LOG INGESTION STREAM LINKED"]);
  const logRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      const msgs = [
        "[LogHarvester] Reading syslog segment 0x01F4...",
        "[CorrelationEngine] Rebuilding kill-chain topology graph.",
        "[ThreatClassifier] LLM Inference cycle complete. Latency: 42ms",
        "[ThreatClassifier] Matched STIX pattern: T1078 Valid Accounts",
        "[System] Kafka queue flushed successfully.",
        "CEF:0|Linux|auditd|1.0|2|Process executed|10|src=10.0.0.5 user=root",
        "[NetworkSensor] Ingress traffic spike detected on port 443",
        "[IncidentWriter] Pushing payload to SOAR playbook...",
      ];
      const rand = msgs[Math.floor(Math.random() * msgs.length)];
      const time = new Date().toISOString().split('T')[1].substring(0, 11);
      setLines(prev => [...prev.slice(-40), `[${time}] ${rand}`]);
    }, 450);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [lines]);

  return (
    <>
      <div className="section-header">
        <h3>Live Raw Stream</h3>
        <span className="agent-count blink">(TAILING EVENT BUS)</span>
      </div>
      <div className="terminal-box" ref={logRef}>
        {lines.map((l, i) => <div key={i} className="line">{l}</div>)}
      </div>
    </>
  );
};

const PageThreatGraph = () => {
  return (
    <>
      <div className="section-header">
        <h3>Threat Topology Map</h3>
        <span className="agent-count blink">(REAL-TIME KILL CHAIN)</span>
      </div>
      <div className="graph-container">
        <div className="graph-node external">
          <div className="node-icon">C2</div>
          <div className="node-text">213.184.248.10</div>
        </div>
        <div className="graph-edge"></div>
        <div className="graph-node compromised">
          <div className="node-icon">API</div>
          <div className="node-text">api-gw-01</div>
        </div>
        <div className="graph-edge"></div>
        <div className="graph-node target">
          <div className="node-icon">DB</div>
          <div className="node-text">prod-db-03</div>
        </div>
        
        <div className="graph-intel">
          <p><span className="data-label">VECTOR:</span> External ➔ DMZ ➔ Internal</p>
          <p><span className="data-label">STIX MAPPING:</span> T1078 Valid Accounts</p>
          <p><span className="data-label">STATUS:</span> Lateral movement observed via SMB</p>
          <p><span className="data-label">LLM CONFIDENCE:</span> <span className="emp">98.4%</span></p>
        </div>
      </div>
    </>
  );
};

// --- APP ROOT --- //

export default function App() {
  const [agents, setAgents] = useState([]);
  const [uptime, setUptime] = useState(0);
  const [activePage, setActivePage] = useState('agents');

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch(`${API}/agents`);
        if (!res.ok) throw new Error("API not reachable");
        const data = await res.json();
        setAgents(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to fetch agents", err);
      }
    };
    fetchAgents();
    const interval = setInterval(fetchAgents, 1500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setUptime(prev => prev + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const formatUptime = (secs) => {
    const h = Math.floor(secs / 3600).toString().padStart(2, '0');
    const m = Math.floor((secs % 3600) / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
  };

  return (
    <div className="soc-layout">
      {/* Sidebar Mock */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-dot"></div>
          <span>SentinelMesh</span>
        </div>
        <nav className="sidebar-nav">
          <button className={activePage === 'agents' ? 'active' : ''} onClick={() => setActivePage('agents')}>Mesh Agents</button>
          <button className={activePage === 'incidents' ? 'active' : ''} onClick={() => setActivePage('incidents')}>Incidents</button>
          <button className={activePage === 'threat-graph' ? 'active' : ''} onClick={() => setActivePage('threat-graph')}>Threat Graph</button>
          <button className={activePage === 'logs' ? 'active' : ''} onClick={() => setActivePage('logs')}>Log Explorer</button>
        </nav>
      </aside>

      <div className="main-wrapper">
        <header className="topbar">
          <div className="topbar-left">
            <h2>SOC Control Platform // <span className="highlight">AMD MI300X Node</span></h2>
          </div>
          <div className="topbar-right">
            <div className="metric">
              <span className="label">SYS UPTIME</span>
              <span className="value">{formatUptime(uptime)}</span>
            </div>
            <div className="metric">
              <span className="label">PIPELINE STATUS</span>
              <span className="value status-ok">ON-LINE</span>
            </div>
          </div>
        </header>

        <main className="content">
          {activePage === 'agents' && <PageAgents agents={agents} />}
          {activePage === 'incidents' && <PageIncidents />}
          {activePage === 'threat-graph' && <PageThreatGraph />}
          {activePage === 'logs' && <PageLogs />}
        </main>
      </div>
    </div>
  );
}
