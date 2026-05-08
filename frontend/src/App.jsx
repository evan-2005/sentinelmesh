import { useState, useEffect } from "react";
import "./App.css";

const API = `http://${window.location.hostname}:8000/api`;

export default function App() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch(`${API}/agents`);
        const data = await res.json();
        setAgents(data);
      } catch (err) {
        console.error("Failed to fetch agents", err);
      }
    };
    fetchAgents();
    const interval = setInterval(fetchAgents, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <header className="header">
        <div className="logo-area">
          <div className="logo-icon"></div>
          <h1>SentinelMesh</h1>
        </div>
        <p className="subtitle">Agentic Threat Detection on AMD ROCm</p>
      </header>

      <main className="main-content">
        <section className="pulse-section">
          <div className="status-indicator">
            <span className="pulse"></span>
            System Active
          </div>
        </section>

        <section className="agents-grid">
          {agents.length === 0 && <div className="loading">Initializing Neural Link...</div>}
          {agents.map((a) => (
            <div key={a.name} className={`agent-card ${a.status === 'busy' ? 'active' : ''}`}>
              <div className="agent-header">
                <h2>{a.name}</h2>
                <span className={`badge ${a.status}`}>{a.status}</span>
              </div>

              <div className="agent-stats">
                <div className="stat">
                  <label>Compute Load</label>
                  <div className="progress-container">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${a.load_pct}%` }}></div>
                    </div>
                    <span className="value">{a.load_pct}%</span>
                  </div>
                </div>
                
                <div className="stat">
                  <label>Events Processed</label>
                  <span className="value highlight">{a.events_processed.toLocaleString()}</span>
                </div>
              </div>

              <div className="agent-task">
                <label>Current Task</label>
                <div className="task-text">{a.current_task}</div>
              </div>
            </div>
          ))}
        </section>
      </main>
      <div className="grid-overlay"></div>
    </div>
  );
}
