import React, { useState, useEffect } from "react";
import "./App.css";

const API = `http://${window.location.hostname}:8000/api`;

export default function App() {
  const [agents, setAgents] = useState([]);
  const [uptime, setUptime] = useState(0);

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
          <a href="#" className="active">Mesh Agents</a>
          <a href="#">Threat Graph</a>
          <a href="#">Incidents</a>
          <a href="#">Log Explorer</a>
          <a href="#">System Metrics</a>
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
          <div className="section-header">
            <h3>Active Mesh Agents</h3>
            {agents.length > 0 && <span className="agent-count">({agents.length} nodes running)</span>}
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
        </main>
      </div>
    </div>
  );
}
