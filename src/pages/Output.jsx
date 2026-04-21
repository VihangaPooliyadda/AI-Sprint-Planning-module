import React, { useEffect, useState } from "react";
import { getSprintPlan } from "../api";

export default function Output() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [filter,  setFilter]  = useState(0); // 0 = all

  useEffect(() => {
    getSprintPlan()
      .then(r => { setData(r.data); setError(null); })
      .catch(() => setError("No sprint plan found. Generate one in the Streamlit app first."))
      .finally(() => setLoading(false));
  }, []);

  const downloadCSV = () => {
    if (!data?.tasks) return;
    const headers = ["task_id","title","sprint_number","priority","priority_confidence_pct",
      "story_points","complexity","estimated_hours","sprint_length_days","team_size"];
    const rows = data.tasks.map(t => headers.map(h => `"${t[h] ?? ""}"`).join(","));
    const csv  = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type:"text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "output_for_member3.csv"; a.click();
  };

  const downloadJSON = () => {
    if (!data?.tasks) return;
    const blob = new Blob([JSON.stringify(data.tasks, null, 2)], { type:"application/json" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "output_for_member3.json"; a.click();
  };

  const tasks   = data?.tasks || [];
  const sprints = [...new Set(tasks.map(t => t.sprint_number))].sort();
  const shown   = filter === 0 ? tasks : tasks.filter(t => t.sprint_number === filter);

  if (loading) return (
    <div className="loading-wrap"><div className="spinner" /></div>
  );

  return (
    <div>
      <div className="page-header fade-up">
        <h1>Output for Member 3</h1>
        <p>Structured sprint plan data ready for Resource Allocation component</p>
      </div>

      {error && <div className="alert alert-warning fade-up">⚠️ {error}</div>}

      {data && (
        <>
          {/* Stats */}
          <div className="stat-grid fade-up">
            {[
              { label:"Total Tasks",   value: tasks.length },
              { label:"Total Sprints", value: data.total_sprints },
              { label:"Story Points",  value: tasks.reduce((a,t)=>a+t.story_points,0), cls:"accent" },
              { label:"Total Hours",   value: tasks.reduce((a,t)=>a+t.estimated_hours,0)+"h", cls:"gold" },
            ].map((s,i) => (
              <div key={i} className={`stat-card ${s.cls||""}`}>
                <div className="stat-value">{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Download + Filter */}
          <div className="fade-up-2" style={{ display:"flex", alignItems:"center",
            gap:"10px", marginBottom:"20px" }}>
            <button className="btn btn-primary" onClick={downloadCSV}>
              ⬇️ Download CSV
            </button>
            <button className="btn btn-ghost" onClick={downloadJSON}>
              ⬇️ Download JSON
            </button>
            <div style={{ marginLeft:"auto", display:"flex", alignItems:"center", gap:"8px" }}>
              <span style={{ fontSize:"12px", color:"var(--muted)", fontWeight:700 }}>SPRINT:</span>
              <button className={`btn ${filter===0?"btn-primary":"btn-ghost"}`}
                onClick={() => setFilter(0)}
                style={{ padding:"6px 12px", fontSize:"12px" }}>ALL</button>
              {sprints.map(s => (
                <button key={s} className={`btn ${filter===s?"btn-primary":"btn-ghost"}`}
                  onClick={() => setFilter(s)}
                  style={{ padding:"6px 12px", fontSize:"12px" }}>S{s}</button>
              ))}
            </div>
          </div>

          {/* Table */}
          <div className="card fade-up-3" style={{ padding:0, overflow:"hidden" }}>
            <div style={{ overflowX:"auto" }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Sprint</th>
                    <th>Task ID</th>
                    <th>Title</th>
                    <th>Priority</th>
                    <th>Confidence</th>
                    <th>Points</th>
                    <th>Complexity</th>
                    <th>Hours</th>
                    <th>Sprint Days</th>
                    <th>Team Size</th>
                  </tr>
                </thead>
                <tbody>
                  {shown.map((t,i) => (
                    <tr key={i}>
                      <td style={{ fontWeight:700, color:"var(--mid)" }}>
                        Sprint {t.sprint_number}
                      </td>
                      <td><code style={{ fontSize:"12px", background:"var(--bg)",
                        padding:"2px 6px", borderRadius:"4px" }}>{t.task_id}</code></td>
                      <td style={{ fontSize:"13px", maxWidth:"200px" }}>{t.title}</td>
                      <td>
                        <span className={`badge badge-${t.priority.toLowerCase()}`}>
                          {t.priority}
                        </span>
                      </td>
                      <td style={{ fontSize:"13px", color:"var(--muted)" }}>
                        {t.priority_confidence_pct}%
                      </td>
                      <td style={{ fontWeight:700 }}>{t.story_points}</td>
                      <td>
                        <span className={`badge ${
                          t.complexity==="LOW"    ? "badge-low"    :
                          t.complexity==="MEDIUM" ? "badge-medium" :
                          "badge-high"
                        }`}>{t.complexity}</span>
                      </td>
                      <td style={{ color:"var(--muted)", fontSize:"13px" }}>
                        {t.estimated_hours}h
                      </td>
                      <td style={{ color:"var(--muted)", fontSize:"13px" }}>
                        {t.sprint_length_days}d
                      </td>
                      <td style={{ color:"var(--muted)", fontSize:"13px" }}>
                        {t.team_size}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* API info */}
          <div className="card fade-up-4" style={{ marginTop:"20px",
            background:"linear-gradient(135deg,#f8faff,#eff6ff)",
            border:"1px solid #dbeafe" }}>
            <h3 style={{ marginBottom:"12px", color:"var(--navy)", fontSize:"14px" }}>
              🔗 API Endpoint for Member 3
            </h3>
            <code style={{ display:"block", background:"var(--navy)", color:"var(--accent)",
              padding:"12px 16px", borderRadius:"8px", fontSize:"13px" }}>
              GET http://localhost:5000/api/sprint-plan
            </code>
            <p style={{ fontSize:"12px", color:"var(--muted)", marginTop:"10px" }}>
              Member 3 can call this endpoint directly to get all tasks in JSON format
              without needing to download files manually.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
