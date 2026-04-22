import React, { useState } from "react";
import { predictPriority, generateSprintPlan } from "../api";

const SAMPLES = [
  { story_id:"US001", title:"Fix critical security vulnerability in login system",  description:"Users can bypass authentication using SQL injection attack on login form",          story_points:8  },
  { story_id:"US002", title:"Add export to PDF feature for reports",                description:"Users need to export their monthly reports as PDF files for sharing",              story_points:5  },
  { story_id:"US003", title:"Update color scheme on dashboard page",                description:"Minor visual update to match new brand guidelines requested by design team",       story_points:2  },
  { story_id:"US004", title:"Payment gateway crashes on checkout",                  description:"Checkout process fails with 500 error for all users blocking all purchases",       story_points:13 },
  { story_id:"US005", title:"Add search filter to user management",                 description:"Allow admins to filter users by role status and registration date",                story_points:5  },
  { story_id:"US006", title:"Fix broken email notifications",                       description:"Email notifications not being sent to users after recent deployment update",       story_points:3  },
  { story_id:"US007", title:"Add dark mode toggle to settings",                     description:"Users requested dark mode option in profile settings for better readability",      story_points:3  },
  { story_id:"US008", title:"Database connection timeout under heavy load",         description:"Server times out when more than 100 users connected simultaneously causing errors",story_points:8  },
  { story_id:"US009", title:"Update help documentation links",                      description:"Several documentation links in help section return 404 errors need updating",      story_points:1  },
  { story_id:"US010", title:"Add two factor authentication for admin users",        description:"Admins need 2FA to improve account security and prevent unauthorized access",       story_points:8  },
];

export default function AddStories() {
  const [stories, setStories] = useState([]);
  const [form, setForm]       = useState({ story_id:"", title:"", description:"", story_points:5 });
  const [loading, setLoading] = useState(false);
  const [alert, setAlert]     = useState(null);

  const showAlert = (msg, type="success") => {
    setAlert({ msg, type });
    setTimeout(() => setAlert(null), 3500);
  };

  const addStory = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.description.trim()) {
      showAlert("Please fill in Title and Description.", "error"); return;
    }
    if (stories.find(s => s.story_id === form.story_id)) {
      showAlert(`Story ${form.story_id} already exists.`, "error"); return;
    }
    setLoading(true);
    try {
      const { data } = await predictPriority(form.title, form.description);
      const story = { ...form, story_points: Number(form.story_points),
        priority: data.priority, confidence: data.confidence };
      setStories(prev => [...prev, story]);
      showAlert(`Story ${form.story_id} added — Priority: ${data.priority} (${data.confidence}%)`);
      setForm({ story_id:`US${String(stories.length + 2).padStart(3,"0")}`,
        title:"", description:"", story_points:5 });
    } catch {
      showAlert("Could not connect to API. Make sure api.py is running.", "error");
    }
    setLoading(false);
  };

  const loadSamples = async () => {
    setLoading(true);
    const result = [];
    for (const s of SAMPLES) {
      try {
        const { data } = await predictPriority(s.title, s.description);
        result.push({ ...s, priority: data.priority, confidence: data.confidence });
      } catch {
        result.push({ ...s, priority:"LOW", confidence:50 });
      }
    }
    setStories(result);
    showAlert("10 sample stories loaded with AI priority predictions!");
    setLoading(false);
  };

  const removeStory = (id) => setStories(prev => prev.filter(s => s.story_id !== id));
  const clearAll    = ()   => { setStories([]); showAlert("All stories cleared.", "info"); };

  return (
    <div>
      <div className="page-header fade-up">
        <h1>Add User Stories</h1>
        <p>Enter stories from Member 1 — AI predicts priority automatically</p>
      </div>

      {alert && (
        <div className={`alert alert-${alert.type} fade-up`}>{alert.msg}</div>
      )}

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"24px" }}>

        {/* Form */}
        <div className="card fade-up-2">
          <h3 style={{ marginBottom:"20px", color:"var(--navy)", fontSize:"15px" }}>
            ➕ Add Single Story
          </h3>
          <form onSubmit={addStory}>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"12px" }}>
              <div className="form-group">
                <label>Story ID</label>
                <input value={form.story_id}
                  onChange={e => setForm(p=>({...p, story_id:e.target.value}))}
                  placeholder="US001" required />
              </div>
              <div className="form-group">
                <label>Story Points</label>
                <input type="number" min="1" max="100" value={form.story_points}
                  onChange={e => setForm(p=>({...p, story_points:e.target.value}))} />
              </div>
            </div>
            <div className="form-group">
              <label>Story Title</label>
              <input value={form.title}
                onChange={e => setForm(p=>({...p, title:e.target.value}))}
                placeholder="e.g. Fix critical login security vulnerability" required />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea value={form.description}
                onChange={e => setForm(p=>({...p, description:e.target.value}))}
                placeholder="Describe the story in detail..." required />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}
              style={{ width:"100%" }}>
              {loading ? "Predicting…" : "➕ Add & Predict Priority"}
            </button>
          </form>

          <div style={{ borderTop:"1px solid var(--border)", margin:"20px 0" }} />

          <button className="btn btn-accent" onClick={loadSamples} disabled={loading}
            style={{ width:"100%" }}>
            {loading ? "Loading…" : "📥 Load 10 Sample Stories"}
          </button>
        </div>

        {/* Stats */}
        <div style={{ display:"flex", flexDirection:"column", gap:"16px" }}>
          <div className="stat-grid" style={{ gridTemplateColumns:"1fr 1fr 1fr" }}>
            <div className="stat-card">
              <div className="stat-value">{stories.length}</div>
              <div className="stat-label">Total</div>
            </div>
            <div className="stat-card accent">
              <div className="stat-value">{stories.filter(s=>s.priority==="HIGH").length}</div>
              <div className="stat-label">HIGH</div>
            </div>
            <div className="stat-card green">
              <div className="stat-value">{stories.reduce((a,s)=>a+s.story_points,0)}</div>
              <div className="stat-label">Points</div>
            </div>
          </div>

          {stories.length > 0 && (
            <div className="card" style={{ flex:1 }}>
              <div style={{ display:"flex", justifyContent:"space-between",
                alignItems:"center", marginBottom:"14px" }}>
                <h3 style={{ color:"var(--navy)", fontSize:"14px" }}>
                  Stories ({stories.length})
                </h3>
                <button
                  className="btn btn-primary"
                  onClick={async () => {
                    if (stories.length === 0) {
                      showAlert("Please add stories first.", "error");
                      return;
                    }
                    try {
                      setLoading(true);
                      const { data } = await generateSprintPlan(stories, {
                        sprint_capacity: 30,
                        sprint_length:   14,
                        team_size:       5,
                      });
                      showAlert(`✅ Sprint plan generated! ${data.total_stories} stories across ${data.total_sprints} sprints. Go to Sprint Plan page to view.`);
                    } catch {
                      showAlert("Could not generate sprint plan. Make sure Railway API is running.", "error");
                    }
                    setLoading(false);
                  }}
                  disabled={loading}
                  style={{ marginBottom: "10px", width: "100%" }}
                >
                  {loading ? "Generating…" : "🚀 Generate Sprint Plan on Server"}
                </button>
                <button className="btn btn-danger" onClick={clearAll}
                  style={{ padding:"6px 12px", fontSize:"12px" }}>
                  🗑 Clear All
                </button>
              </div>
              <div style={{ maxHeight:"360px", overflowY:"auto" }}>
                {stories.map((s, i) => (
                  <div key={i} style={{ display:"flex", alignItems:"center",
                    justifyContent:"space-between", padding:"10px 12px",
                    marginBottom:"6px", borderRadius:"8px", background:"var(--bg)",
                    border:"1px solid var(--border)" }}>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ display:"flex", alignItems:"center", gap:"8px",
                        marginBottom:"2px" }}>
                        <span style={{ fontSize:"11px", fontWeight:700,
                          color:"var(--muted)" }}>{s.story_id}</span>
                        <span className={`badge badge-${s.priority.toLowerCase()}`}>
                          {s.priority} {s.confidence}%
                        </span>
                        <span style={{ fontSize:"11px", color:"var(--muted)" }}>
                          {s.story_points}pts
                        </span>
                      </div>
                      <div style={{ fontSize:"12px", color:"var(--text)",
                        overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                        {s.title}
                      </div>
                    </div>
                    <button className="btn btn-ghost" onClick={() => removeStory(s.story_id)}
                      style={{ padding:"4px 8px", fontSize:"11px", marginLeft:"8px" }}>✕</button>
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
