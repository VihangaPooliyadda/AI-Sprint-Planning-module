import { replanFull } from "../api";
import React, { useState } from "react";
import { triggerReplan, getSprintPlan } from "../api";

const CHANGE_TYPES = ["NEW_STORY_ADDED","STORY_REMOVED","STORY_MODIFIED","PRIORITY_CHANGED"];
const URGENCIES    = ["CRITICAL","HIGH","MEDIUM","LOW"];

export default function Replanning() {
  const [form, setForm] = useState({
    change_type: "NEW_STORY_ADDED",
    story_id:    "",
    title:       "",
    description: "",
    story_points: 8,
    urgency:     "CRITICAL",
    reason:      "",
  });
  const [loading, setLoading] = useState(false);
  const [alert,   setAlert]   = useState(null);
  const [history, setHistory] = useState([]);

  const showAlert = (msg, type="success") => {
    setAlert({ msg, type });
    setTimeout(() => setAlert(null), 4000);
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!form.story_id.trim()) {
      showAlert("Please enter a Story ID.", "error");
      return;
    }
    setLoading(true);
    try {
      const { data } = await replanFull({
        change_type:  form.change_type,
        story_id:     form.story_id,
        title:        form.title,
        description:  form.description,
        story_points: Number(form.story_points),
        urgency:      form.urgency,
        reason:       form.reason,
      });
      setHistory(prev => [{
        ...form, timestamp: new Date().toLocaleTimeString()
      }, ...prev]);
      showAlert(`✅ ${form.story_id} applied! Sprint plan updated automatically. Go to Sprint Plan page to see changes.`);
      setForm(p => ({ ...p, story_id:"", title:"", description:"", reason:"" }));
    } catch (err) {
      const msg = err.response?.data?.message || "Could not connect to API. Make sure api.py is running.";
      showAlert(msg, "error");
    }
    setLoading(false);
  };
  
  const typeColors = {
    "NEW_STORY_ADDED":  "#f0fdf4",
    "STORY_REMOVED":    "#fef2f2",
    "STORY_MODIFIED":   "#fffbeb",
    "PRIORITY_CHANGED": "#eff6ff",
  };
  const typeBorders = {
    "NEW_STORY_ADDED":  "#bbf7d0",
    "STORY_REMOVED":    "#fecaca",
    "STORY_MODIFIED":   "#fde68a",
    "PRIORITY_CHANGED": "#bfdbfe",
  };
  const typeIcons = {
    "NEW_STORY_ADDED":  "➕",
    "STORY_REMOVED":    "🗑",
    "STORY_MODIFIED":   "✏️",
    "PRIORITY_CHANGED": "🔄",
  };

  return (
    <div>
      <div className="page-header fade-up">
        <h1>Dynamic Re-planning</h1>
        <p>Handle scope change alerts from Member 4 (Change Management)</p>
      </div>

      {alert && (
        <div className={`alert alert-${alert.type} fade-up`}>{alert.msg}</div>
      )}

      <div className="alert alert-info fade-up" style={{ marginBottom:"24px" }}>
        ℹ️ After applying a change, go to the <strong>Sprint Plan</strong> page and click
        Refresh to see the updated allocation.
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"24px" }}>

        {/* Form */}
        <div className="card fade-up-2">
          <h3 style={{ marginBottom:"20px", color:"var(--navy)", fontSize:"15px" }}>
            📨 Change Alert from Member 4
          </h3>
          <form onSubmit={submit}>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"12px" }}>
              <div className="form-group">
                <label>Change Type</label>
                <select value={form.change_type}
                  onChange={e => setForm(p=>({...p, change_type:e.target.value}))}>
                  {CHANGE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Urgency</label>
                <select value={form.urgency}
                  onChange={e => setForm(p=>({...p, urgency:e.target.value}))}>
                  {URGENCIES.map(u => <option key={u} value={u}>{u}</option>)}
                </select>
              </div>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"12px" }}>
              <div className="form-group">
                <label>Story ID</label>
                <input value={form.story_id}
                  onChange={e => setForm(p=>({...p, story_id:e.target.value}))}
                  placeholder="e.g. US011" required />
              </div>
              <div className="form-group">
                <label>Story Points</label>
                <input type="number" min="1" max="100" value={form.story_points}
                  onChange={e => setForm(p=>({...p, story_points:Number(e.target.value)}))} />
              </div>
            </div>

            <div className="form-group">
              <label>Story Title</label>
              <input value={form.title}
                onChange={e => setForm(p=>({...p, title:e.target.value}))}
                placeholder="Title of new or modified story" />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea value={form.description}
                onChange={e => setForm(p=>({...p, description:e.target.value}))}
                placeholder="Describe the change…" />
            </div>

            <div className="form-group">
              <label>Reason for Change</label>
              <input value={form.reason}
                onChange={e => setForm(p=>({...p, reason:e.target.value}))}
                placeholder="Why is this change happening?" />
            </div>

            <button className="btn btn-primary" type="submit" disabled={loading}
              style={{ width:"100%" }}>
              {loading ? "Applying…" : "⚡ Apply Change & Log"}
            </button>
          </form>
        </div>

        {/* Change Type Guide + History */}
        <div style={{ display:"flex", flexDirection:"column", gap:"16px" }}>
          <div className="card fade-up-3">
            <h3 style={{ marginBottom:"14px", color:"var(--navy)", fontSize:"14px" }}>
              📋 Change Type Guide
            </h3>
            {[
              { type:"NEW_STORY_ADDED",  desc:"A new user story is added to the backlog" },
              { type:"STORY_REMOVED",    desc:"An existing story is removed from scope"  },
              { type:"STORY_MODIFIED",   desc:"Story points or details have changed"      },
              { type:"PRIORITY_CHANGED", desc:"Priority level of a story has changed"     },
            ].map((item,i) => (
              <div key={i} style={{ display:"flex", gap:"10px", marginBottom:"10px",
                padding:"10px 12px", borderRadius:"8px",
                background: typeColors[item.type],
                border: `1px solid ${typeBorders[item.type]}` }}>
                <span>{typeIcons[item.type]}</span>
                <div>
                  <div style={{ fontSize:"12px", fontWeight:700,
                    fontFamily:"var(--font-display)", color:"var(--navy)" }}>
                    {item.type}
                  </div>
                  <div style={{ fontSize:"12px", color:"var(--muted)" }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>

          {history.length > 0 && (
            <div className="card fade-up-4">
              <h3 style={{ marginBottom:"14px", color:"var(--navy)", fontSize:"14px" }}>
                🕐 Session Change History
              </h3>
              <div style={{ maxHeight:"220px", overflowY:"auto" }}>
                {history.map((h,i) => (
                  <div key={i} style={{ display:"flex", alignItems:"flex-start",
                    gap:"10px", marginBottom:"8px", padding:"10px 12px",
                    borderRadius:"8px", background: typeColors[h.change_type],
                    border: `1px solid ${typeBorders[h.change_type]}` }}>
                    <span style={{ fontSize:"16px" }}>{typeIcons[h.change_type]}</span>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ fontSize:"12px", fontWeight:700,
                        color:"var(--navy)" }}>{h.story_id}</div>
                      <div style={{ fontSize:"11px", color:"var(--muted)" }}>
                        {h.change_type} • {h.timestamp}
                      </div>
                      {h.reason && (
                        <div style={{ fontSize:"11px", color:"var(--text)",
                          marginTop:"2px" }}>{h.reason}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
