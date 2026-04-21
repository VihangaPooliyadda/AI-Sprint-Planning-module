import React, { useEffect, useState } from "react";
import { healthCheck, getSprintPlan } from "../api";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [stats,  setStats]  = useState(null);
  const [error,  setError]  = useState(false);

  useEffect(() => {
    healthCheck()
      .then(r => setHealth(r.data))
      .catch(() => setError(true));

    getSprintPlan()
      .then(r => {
        const tasks = r.data.tasks || [];
        setStats({
          total:   tasks.length,
          high:    tasks.filter(t => t.priority === "HIGH").length,
          low:     tasks.filter(t => t.priority === "LOW").length,
          sprints: r.data.total_sprints || 0,
          points:  tasks.reduce((a, t) => a + (t.story_points || 0), 0),
          hours:   tasks.reduce((a, t) => a + (t.estimated_hours || 0), 0),
        });
      })
      .catch(() => {});
  }, []);

  return (
    <div>
      <div className="page-header fade-up">
        <h1>Dashboard</h1>
        <p>AI-Powered Sprint Planning and Allocation — Member 2 Overview</p>
      </div>

      {error && (
        <div className="alert alert-error fade-up">
          ⚠️ Cannot reach the Flask API. Make sure <strong>api.py</strong> is running on port 5000.
        </div>
      )}

      {/* Stats */}
      <div className="stat-grid">
        {[
          { label: "Total Stories",     value: stats?.total   ?? "—", cls: ""       },
          { label: "HIGH Priority",     value: stats?.high    ?? "—", cls: "accent" },
          { label: "LOW Priority",      value: stats?.low     ?? "—", cls: "green"  },
          { label: "Sprints Generated", value: stats?.sprints ?? "—", cls: "gold"   },
          { label: "Total Story Points",value: stats?.points  ?? "—", cls: ""       },
          { label: "Estimated Hours",   value: stats?.hours   ?? "—", cls: "accent" },
        ].map((s, i) => (
          <div key={i} className={`stat-card ${s.cls} fade-up`} style={{ animationDelay: `${i * .07}s` }}>
            <div className="stat-value">{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>

        {/* System Status */}
        <div className="card fade-up-2">
          <h3 style={{ marginBottom: "16px", color: "var(--navy)", fontSize: "15px" }}>
            🔧 System Status
          </h3>
          {health ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {[
                { ok: true,                     label: "Flask API Running"       },
                { ok: health.models_loaded,     label: "ML Models Loaded"        },
                { ok: health.sprint_plan_ready, label: "Sprint Plan Ready"       },
              ].map((s, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: "10px",
                  padding: "10px 14px", borderRadius: "8px",
                  background: s.ok ? "#f0fdf4" : "#fef2f2",
                  border: `1px solid ${s.ok ? "#bbf7d0" : "#fecaca"}` }}>
                  <span style={{ fontSize: "16px" }}>{s.ok ? "✅" : "❌"}</span>
                  <span style={{ fontSize: "13px", fontWeight: 500, color: s.ok ? "#15803d" : "#dc2626" }}>
                    {s.label}
                  </span>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="alert alert-error">API not reachable</div>
          ) : (
            <div className="loading-wrap"><div className="spinner" /></div>
          )}
        </div>

        {/* Pipeline */}
        <div className="card fade-up-3">
          <h3 style={{ marginBottom: "16px", color: "var(--navy)", fontSize: "15px" }}>
            🔄 Group Pipeline
          </h3>
          {[
            { n: "1", label: "Requirement Elicitation & User Stories", you: false },
            { n: "2", label: "Sprint Planning & Allocation",            you: true  },
            { n: "3", label: "Resource Allocation & Man Hours",         you: false },
            { n: "4", label: "Change Management & Scope Creep",         you: false },
          ].map((m, i) => (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: "12px",
              padding: "10px 14px", marginBottom: "6px",
              borderRadius: "8px",
              background: m.you ? "linear-gradient(90deg,#eff6ff,#dbeafe)" : "var(--bg)",
              border: m.you ? "1.5px solid #93c5fd" : "1px solid var(--border)",
            }}>
              <div style={{
                width: "28px", height: "28px", borderRadius: "50%", flexShrink: 0,
                background: m.you ? "var(--mid)" : "var(--border)",
                color: m.you ? "#fff" : "var(--muted)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "12px",
              }}>{m.n}</div>
              <span style={{ fontSize: "13px", fontWeight: m.you ? 700 : 400,
                color: m.you ? "var(--navy)" : "var(--muted)" }}>
                {m.label} {m.you && <span style={{ color: "var(--mid)", fontSize: "11px" }}>(You)</span>}
              </span>
            </div>
          ))}
        </div>

      </div>

      {/* Model Performance Summary */}
      <div className="card fade-up-4" style={{ marginTop: "20px" }}>
        <h3 style={{ marginBottom: "16px", color: "var(--navy)", fontSize: "15px" }}>
          📊 Model Performance Summary
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          {[
            { title: "Priority Prediction",  model: "Random Forest + TF-IDF", metric: "Accuracy",  value: "67.58%", sub: "F1 Score: 0.673" },
            { title: "Effort Estimation",     model: "Random Forest Regressor", metric: "R² Score",  value: "0.992",  sub: "MAE: 1.78 pts"  },
          ].map((m, i) => (
            <div key={i} style={{ padding: "16px", borderRadius: "10px",
              background: "linear-gradient(135deg,#f8faff,#eff6ff)",
              border: "1px solid #dbeafe" }}>
              <div style={{ fontSize: "11px", color: "var(--muted)", fontWeight: 700,
                textTransform: "uppercase", letterSpacing: ".5px", marginBottom: "4px" }}>
                {m.title}
              </div>
              <div style={{ fontSize: "13px", color: "var(--navy)", marginBottom: "8px" }}>{m.model}</div>
              <div style={{ fontSize: "11px", color: "var(--muted)", marginBottom: "2px" }}>{m.metric}</div>
              <div style={{ fontSize: "26px", fontFamily: "var(--font-display)",
                fontWeight: 800, color: "var(--mid)" }}>{m.value}</div>
              <div style={{ fontSize: "11px", color: "var(--muted)", marginTop: "2px" }}>{m.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
