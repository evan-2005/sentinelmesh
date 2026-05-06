// SentinelMesh React Dashboard
// Entry point — replace with full dashboard component from the prototype
import { useState, useEffect } from "react";

const API = "http://localhost:8000/api";

export default function App() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    fetch(`${API}/agents`)
      .then((r) => r.json())
      .then(setAgents)
      .catch(console.error);
  }, []);

  return (
    <div style={{ fontFamily: "monospace", padding: "2rem" }}>
      <h1>SentinelMesh</h1>
      <p>Agentic threat detection on AMD ROCm</p>
      <h2>Agent Status</h2>
      {agents.map((a) => (
        <div key={a.name} style={{ marginBottom: "1rem", padding: "1rem", border: "1px solid #ccc" }}>
          <strong>{a.name}</strong> — {a.status}<br />
          Task: {a.current_task}<br />
          Load: {a.load_pct}%
        </div>
      ))}
      {/* TODO: wire in full SentinelMesh dashboard from prototype */}
    </div>
  );
}
