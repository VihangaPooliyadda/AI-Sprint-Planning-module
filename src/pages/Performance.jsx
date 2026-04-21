import React, { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const PRIORITY_MODELS = [
  { model:"Random Forest",      accuracy:67.58, f1:0.673, rank:"🥇 Best" },
  { model:"Logistic Regression",accuracy:66.77, f1:0.666, rank:"🥈 2nd"  },
  { model:"Linear SVM",         accuracy:66.51, f1:0.664, rank:"🥉 3rd"  },
  { model:"Naive Bayes",        accuracy:65.35, f1:0.650, rank:"4th"      },
];

const EFFORT_MODELS = [
  { model:"Random Forest",   mae:1.78, r2:0.992, cv:0.794, rank:"🥇 Best" },
  { model:"Linear Regression",mae:1.96, r2:0.994, cv:"N/A",  rank:"🥈 2nd" },
];

const FEATURE_IMP = [
  { feature:"Initial Estimate Sum", importance:93.1 },
  { feature:"Completed Issues",     importance:5.1  },
  { feature:"Points per Dev/Day",   importance:0.4  },
  { feature:"Total Issues",         importance:0.3  },
  { feature:"Sprint Length",        importance:0.2  },
  { feature:"No. of Developers",    importance:0.2  },
  { feature:"Completion Rate",      importance:0.0  },
];

const CONFUSION = [
  { actual:"Actual LOW",  predLow:6697, predHigh:2250 },
  { actual:"Actual HIGH", predLow:3114, predHigh:4483 },
];

const tabs = ["🎯 Priority Prediction","⏱ Effort Estimation","📋 Datasets"];

export default function Performance() {
  const [tab, setTab] = useState(0);

  return (
    <div>
      <div className="page-header fade-up">
        <h1>Model Performance</h1>
        <p>Evaluation results for Priority Prediction and Effort Estimation models</p>
      </div>

      {/* Tab bar */}
      <div className="fade-up" style={{ display:"flex", gap:"8px", marginBottom:"24px",
        borderBottom:"2px solid var(--border)", paddingBottom:"0" }}>
        {tabs.map((t,i) => (
          <button key={i} onClick={() => setTab(i)}
            style={{ padding:"10px 20px", border:"none", background:"none",
              fontFamily:"var(--font-display)", fontWeight:700, fontSize:"13px",
              cursor:"pointer", color: tab===i ? "var(--mid)" : "var(--muted)",
              borderBottom: tab===i ? "2px solid var(--mid)" : "2px solid transparent",
              marginBottom:"-2px", transition:"all .2s" }}>
            {t}
          </button>
        ))}
      </div>

      {/* Priority Prediction Tab */}
      {tab === 0 && (
        <div>
          {/* Metrics */}
          <div className="stat-grid fade-up">
            {[
              { label:"Accuracy",         value:"67.58%", cls:"accent" },
              { label:"F1 Score",         value:"0.673",  cls:""       },
              { label:"Training Samples", value:"66,175", cls:""       },
              { label:"Test Samples",     value:"16,544", cls:"gold"   },
            ].map((s,i) => (
              <div key={i} className={`stat-card ${s.cls}`}>
                <div className="stat-value">{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>

          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"20px" }}>

            {/* Model comparison chart */}
            <div className="card fade-up-2">
              <h3 style={{ marginBottom:"16px", color:"var(--navy)", fontSize:"14px" }}>
                Model Comparison — Accuracy
              </h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={PRIORITY_MODELS} margin={{ top:0, right:0, left:-20, bottom:0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f4f9" />
                  <XAxis dataKey="model" tick={{ fontSize:11 }} />
                  <YAxis domain={[64, 68.5]} tick={{ fontSize:11 }} />
                  <Tooltip formatter={(v) => `${v}%`} />
                  <Bar dataKey="accuracy" fill="#2563a8" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Confusion matrix */}
            <div className="card fade-up-3">
              <h3 style={{ marginBottom:"16px", color:"var(--navy)", fontSize:"14px" }}>
                Confusion Matrix (Test Set)
              </h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th></th>
                    <th>Predicted LOW</th>
                    <th>Predicted HIGH</th>
                  </tr>
                </thead>
                <tbody>
                  {CONFUSION.map((r,i) => (
                    <tr key={i}>
                      <td style={{ fontWeight:700, color:"var(--navy)" }}>{r.actual}</td>
                      <td style={{ color: i===0 ? "#16a34a" : "#dc2626",
                        fontWeight:700, fontSize:"15px" }}>{r.predLow.toLocaleString()}</td>
                      <td style={{ color: i===1 ? "#16a34a" : "#dc2626",
                        fontWeight:700, fontSize:"15px" }}>{r.predHigh.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p style={{ fontSize:"12px", color:"var(--muted)", marginTop:"10px" }}>
                ✅ Correctly classified: 6,697 + 4,483 = <strong>11,180</strong> out of 16,544
              </p>
            </div>

          </div>

          {/* Full comparison table */}
          <div className="card fade-up-4" style={{ marginTop:"20px" }}>
            <h3 style={{ marginBottom:"16px", color:"var(--navy)", fontSize:"14px" }}>
              Full Model Comparison Table
            </h3>
            <table className="data-table">
              <thead>
                <tr><th>Model</th><th>Accuracy</th><th>F1 Score</th><th>Rank</th></tr>
              </thead>
              <tbody>
                {PRIORITY_MODELS.map((m,i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: i===0 ? 700 : 400,
                      color: i===0 ? "var(--mid)" : "var(--text)" }}>{m.model}</td>
                    <td style={{ fontWeight:700 }}>{m.accuracy}%</td>
                    <td>{m.f1}</td>
                    <td>{m.rank}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Effort Estimation Tab */}
      {tab === 1 && (
        <div>
          <div className="stat-grid fade-up">
            {[
              { label:"R² Score",         value:"0.992",  cls:"green"  },
              { label:"MAE (story pts)",  value:"1.78",   cls:"accent" },
              { label:"CV R² Average",    value:"0.794",  cls:""       },
              { label:"Training Samples", value:"190",    cls:"gold"   },
            ].map((s,i) => (
              <div key={i} className={`stat-card ${s.cls}`}>
                <div className="stat-value">{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>

          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"20px" }}>

            {/* Feature importance */}
            <div className="card fade-up-2">
              <h3 style={{ marginBottom:"16px", color:"var(--navy)", fontSize:"14px" }}>
                Feature Importance
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={FEATURE_IMP} layout="vertical"
                  margin={{ top:0, right:10, left:10, bottom:0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f4f9" />
                  <XAxis type="number" tick={{ fontSize:10 }}
                    tickFormatter={v => `${v}%`} />
                  <YAxis type="category" dataKey="feature" width={140} tick={{ fontSize:10 }} />
                  <Tooltip formatter={v => `${v}%`} />
                  <Bar dataKey="importance" fill="#38bdf8" radius={[0,4,4,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Effort model comparison */}
            <div className="card fade-up-3">
              <h3 style={{ marginBottom:"16px", color:"var(--navy)", fontSize:"14px" }}>
                Effort Model Comparison
              </h3>
              <table className="data-table">
                <thead>
                  <tr><th>Model</th><th>MAE</th><th>R²</th><th>CV R²</th><th>Rank</th></tr>
                </thead>
                <tbody>
                  {EFFORT_MODELS.map((m,i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: i===0 ? 700 : 400,
                        color: i===0 ? "var(--mid)" : "var(--text)" }}>{m.model}</td>
                      <td style={{ fontWeight:700 }}>{m.mae}</td>
                      <td>{m.r2}</td>
                      <td>{m.cv}</td>
                      <td>{m.rank}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div style={{ marginTop:"20px", padding:"16px", borderRadius:"10px",
                background:"linear-gradient(135deg,#f0fdf4,#dcfce7)",
                border:"1px solid #bbf7d0" }}>
                <div style={{ fontSize:"11px", color:"#16a34a", fontWeight:700,
                  marginBottom:"4px", textTransform:"uppercase" }}>
                  Top Feature
                </div>
                <div style={{ fontSize:"15px", fontFamily:"var(--font-display)",
                  fontWeight:800, color:"var(--navy)" }}>
                  Initial Estimate Sum
                </div>
                <div style={{ fontSize:"28px", fontFamily:"var(--font-display)",
                  fontWeight:800, color:"#16a34a" }}>93.1%</div>
                <div style={{ fontSize:"12px", color:"var(--muted)" }}>
                  of predictive importance
                </div>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* Datasets Tab */}
      {tab === 2 && (
        <div>
          <div className="card fade-up" style={{ marginBottom:"20px" }}>
            <h3 style={{ marginBottom:"16px", color:"var(--navy)", fontSize:"14px" }}>
              Datasets Used in This Research
            </h3>
            <table className="data-table">
              <thead>
                <tr><th>Dataset</th><th>Source</th><th>Size</th><th>Used For</th></tr>
              </thead>
              <tbody>
                {[
                  { name:"GitHub Issues (cross-project_norm.csv)", source:"Izadi et al. 2021 / Zenodo", size:"82,719 issues", use:"Priority Prediction" },
                  { name:"Aurora Sprints",   source:"Agile Scrum Sprint Velocity Dataset", size:"40 sprints",  use:"Effort Estimation" },
                  { name:"MESO Sprints",     source:"Agile Scrum Sprint Velocity Dataset", size:"96 sprints",  use:"Effort Estimation" },
                  { name:"Spring XD Sprints",source:"Agile Scrum Sprint Velocity Dataset", size:"66 sprints",  use:"Effort Estimation" },
                  { name:"Usergrid Sprints", source:"Agile Scrum Sprint Velocity Dataset", size:"36 sprints",  use:"Effort Estimation" },
                ].map((d,i) => (
                  <tr key={i}>
                    <td style={{ fontWeight:500 }}>{d.name}</td>
                    <td style={{ fontSize:"12px", color:"var(--muted)" }}>{d.source}</td>
                    <td><span className="badge badge-medium">{d.size}</span></td>
                    <td><span className="badge badge-low">{d.use}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card fade-up-2" style={{
            background:"linear-gradient(135deg,#f8faff,#eff6ff)",
            border:"1px solid #dbeafe" }}>
            <h3 style={{ marginBottom:"12px", color:"var(--navy)", fontSize:"14px" }}>
              Research Contribution
            </h3>
            <p style={{ fontSize:"13px", color:"var(--text)", lineHeight:1.7,
              fontStyle:"italic" }}>
              "No existing study proposes a single integrated pipeline that combines priority
              prediction, effort estimation, and sprint allocation within one unified workflow
              that also supports dynamic re-planning in response to real-time scope change
              events. This research addresses that gap."
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
