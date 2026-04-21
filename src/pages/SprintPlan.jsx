import React, { useEffect, useState } from "react";
import { getSprintPlan } from "../api";

export default function SprintPlan() {
  const [plan,     setPlan]     = useState(null);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(null);
  const [open,     setOpen]     = useState({});
  const [filter,   setFilter]   = useState("ALL");

  const load = () => {
    setLoading(true);
    getSprintPlan()
      .then(r => {
        // Group tasks by sprint
        const tasks = r.data.tasks || [];
        const grouped = {};
        tasks.forEach(t => {
          if (!grouped[t.sprint_number]) grouped[t.sprint_number] = [];
          grouped[t.sprint_number].push(t);
        });
        setPlan({ meta: r.data, grouped });
        const init = {};
        Object.keys(grouped).forEach(k => init[k] = true);
        setOpen(init);
        setError(null);
      })
      .catch(() => setError("No sprint plan found. Please generate one from the Streamlit app."))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const toggle = (n) => setOpen(p => ({ ...p, [n]: !p[n] }));

  const filtered = (tasks) =>
    filter === "ALL" ? tasks : tasks.filter(t => t.priority === filter);

  if (loading) return (
    <div className="loading-wrap">
      <div className="spinner" />
      <span style={{ color:"var(--muted)", fontSize:"14px" }}>Loading sprint plan…</span>
    </div>
  );

  return (
    <div>
      <div className="page-header fade-up">
        <h1>Sprint Plan</h1>
        <p>Auto-generated using Greedy Bin-Packing — HIGH priority stories first</p>
      </div>

      {error && (
        <div className="alert alert-warning fade-up">
          ⚠️ {error}
        </div>
      )}

      {plan && (
        <>
          {/* Summary */}
          <div className="stat-grid fade-up">
            {[
              { label:"Total Tasks",    value: plan.meta.total_tasks    },
              { label:"Total Sprints",  value: plan.meta.total_sprints  },
              { label:"HIGH Priority",  value: (plan.meta.tasks||[]).filter(t=>t.priority==="HIGH").length, cls:"accent" },
              { label:"Total Hours",    value: (plan.meta.tasks||[]).reduce((a,t)=>a+t.estimated_hours,0)+"h", cls:"gold" },
            ].map((s,i) => (
              <div key={i} className={`stat-card ${s.cls||""}`}>
                <div className="stat-value">{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Filter + refresh */}
          <div className="fade-up-2" style={{ display:"flex", alignItems:"center",
            gap:"10px", marginBottom:"20px" }}>
            <span style={{ fontSize:"12px", color:"var(--muted)", fontWeight:700 }}>FILTER:</span>
            {["ALL","HIGH","LOW"].map(f => (
              <button key={f} className={`btn ${filter===f?"btn-primary":"btn-ghost"}`}
                onClick={() => setFilter(f)}
                style={{ padding:"6px 14px", fontSize:"12px" }}>{f}</button>
            ))}
            <button className="btn btn-ghost" onClick={load}
              style={{ marginLeft:"auto", padding:"6px 14px", fontSize:"12px" }}>
              ↻ Refresh
            </button>
          </div>

          {/* Sprint blocks */}
          {Object.entries(plan.grouped).map(([sprintNum, tasks]) => {
            const shown      = filtered(tasks);
            const totalPts   = tasks.reduce((a,t)=>a+t.story_points,0);
            const capacity   = 30;
            const pct        = Math.min(Math.round(totalPts/capacity*100),100);
            const highCount  = tasks.filter(t=>t.priority==="HIGH").length;
            const lowCount   = tasks.filter(t=>t.priority==="LOW").length;
            const isOpen     = open[sprintNum];

            return (
              <div key={sprintNum} className="sprint-block fade-up">
                <div className="sprint-block-header" onClick={() => toggle(sprintNum)}>
                  <h3>Sprint {sprintNum}</h3>
                  <div className="sprint-meta">
                    <span>🔴 {highCount} HIGH</span>
                    <span>🟢 {lowCount} LOW</span>
                    <span>📦 {totalPts}/{capacity} pts ({pct}%)</span>
                    <span style={{ color:"var(--accent)" }}>{isOpen ? "▲" : "▼"}</span>
                  </div>
                </div>

                {/* Progress bar */}
                <div style={{ padding:"10px 20px", background:"var(--navy)",
                  paddingTop:0, paddingBottom:"12px" }}>
                  <div className="progress-bar-wrap">
                    <div className="progress-bar-fill" style={{ width:`${pct}%` }} />
                  </div>
                </div>

                {isOpen && (
                  <div className="sprint-block-body">
                    {shown.length === 0 ? (
                      <div style={{ padding:"20px", color:"var(--muted)", fontSize:"13px",
                        textAlign:"center" }}>No {filter} priority tasks in this sprint.</div>
                    ) : (
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Priority</th>
                            <th>Confidence</th>
                            <th>Points</th>
                            <th>Complexity</th>
                            <th>Hours</th>
                          </tr>
                        </thead>
                        <tbody>
                          {shown.map((t,i) => (
                            <tr key={i}>
                              <td><code style={{ fontSize:"12px",
                                background:"var(--bg)", padding:"2px 6px",
                                borderRadius:"4px" }}>{t.task_id}</code></td>
                              <td style={{ maxWidth:"260px" }}>
                                <div style={{ fontSize:"13px", fontWeight:500 }}>{t.title}</div>
                              </td>
                              <td>
                                <span className={`badge badge-${t.priority.toLowerCase()}`}>
                                  {t.priority}
                                </span>
                              </td>
                              <td style={{ fontSize:"13px", color:"var(--muted)" }}>
                                {t.priority_confidence_pct}%
                              </td>
                              <td style={{ fontWeight:700, color:"var(--navy)" }}>
                                {t.story_points}
                              </td>
                              <td>
                                <span className={`badge ${
                                  t.complexity==="LOW"       ? "badge-low"    :
                                  t.complexity==="MEDIUM"    ? "badge-medium" :
                                  "badge-high"
                                }`}>{t.complexity}</span>
                              </td>
                              <td style={{ fontSize:"13px", color:"var(--muted)" }}>
                                {t.estimated_hours}h
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </>
      )}
    </div>
  );
}
