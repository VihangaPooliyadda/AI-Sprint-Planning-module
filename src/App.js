import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Dashboard   from "./pages/Dashboard";
import AddStories  from "./pages/AddStories";
import SprintPlan  from "./pages/SprintPlan";
import Replanning  from "./pages/Replanning";
import Output      from "./pages/Output";
import Performance from "./pages/Performance";
import "./App.css";

const NAV = [
  { to: "/",            icon: "⬡", label: "Dashboard"    },
  { to: "/stories",     icon: "✦", label: "Add Stories"  },
  { to: "/sprint-plan", icon: "◈", label: "Sprint Plan"  },
  { to: "/replan",      icon: "↺", label: "Re-planning"  },
  { to: "/output",      icon: "⇡", label: "Output"       },
  { to: "/performance", icon: "◉", label: "Performance"  },
];

export default function App() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Router>
      <div className="app-shell">

        {/* ── Sidebar ── */}
        <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
          <div className="sidebar-header">
            <div className="sidebar-logo">
              <span className="logo-icon">◈</span>
              {!collapsed && <span className="logo-text">SprintAI</span>}
            </div>
            <button className="collapse-btn" onClick={() => setCollapsed(c => !c)}>
              {collapsed ? "›" : "‹"}
            </button>
          </div>

          {!collapsed && (
            <div className="sidebar-subtitle">
              Sprint Planning System<br />
              <span>IT22134844</span>
            </div>
          )}

          <nav className="sidebar-nav">
            {NAV.map(({ to, icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
              >
                <span className="nav-icon">{icon}</span>
                {!collapsed && <span className="nav-label">{label}</span>}
              </NavLink>
            ))}
          </nav>

          {!collapsed && (
            <div className="sidebar-footer">
              <div className="footer-badge">R26-ISE-005</div>
              <div className="footer-name">T.M.V.M.B. Pooliyadda</div>
            </div>
          )}
        </aside>

        {/* ── Main ── */}
        <main className="main-content">
          <Routes>
            <Route path="/"            element={<Dashboard />}   />
            <Route path="/stories"     element={<AddStories />}  />
            <Route path="/sprint-plan" element={<SprintPlan />}  />
            <Route path="/replan"      element={<Replanning />}  />
            <Route path="/output"      element={<Output />}      />
            <Route path="/performance" element={<Performance />} />
          </Routes>
        </main>

      </div>
    </Router>
  );
}
