"""
============================================================
  SPRINT PLANNING API — Member 2: T.M.V.M.B. Pooliyadda
  IT22134844 | R26-ISE-005
  
  This API provides sprint plan data for Member 3
  (Resource Allocation Component).
  
  Base URL : http://localhost:5000
  
  ENDPOINTS:
    GET  /api/health
    GET  /api/sprint-plan
    GET  /api/sprint-plan/<sprint_number>
    GET  /api/stories
    POST /api/predict-priority
    POST /api/replan
============================================================
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import pickle
import sqlite3
import os
import json
from datetime import datetime

# ── App setup ─────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Member 3's system

# ── Paths ─────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join("/tmp", "sprint_planning.db")
OUTPUT_JSON = os.path.join(BASE, "output_for_member3.json")
MODEL_PKL   = os.path.join(BASE, "priority_model.pkl")
TFIDF_PKL   = os.path.join(BASE, "priority_tfidf.pkl")

# ── Load ML models ────────────────────────────────────────
try:
    with open(MODEL_PKL, "rb") as f:
        priority_model = pickle.load(f)
    with open(TFIDF_PKL, "rb") as f:
        tfidf = pickle.load(f)
    MODELS_LOADED = True
    print("✅ ML models loaded successfully")
except Exception as e:
    MODELS_LOADED = False
    print(f"⚠️  ML models not loaded: {e}")

# ═══════════════════════════════════════════════════════════
# DATABASE HELPERS
# ═══════════════════════════════════════════════════════════

def get_db():
    """Get SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS user_stories (
            story_id        TEXT PRIMARY KEY,
            title           TEXT NOT NULL,
            description     TEXT,
            story_points    INTEGER,
            priority        TEXT,
            confidence      REAL,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sprint_plans (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            sprint_number   INTEGER,
            story_id        TEXT,
            title           TEXT,
            priority        TEXT,
            story_points    INTEGER,
            estimated_hours INTEGER,
            sprint_length   INTEGER DEFAULT 14,
            team_size       INTEGER DEFAULT 5,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS change_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            change_type     TEXT,
            story_id        TEXT,
            old_value       TEXT,
            new_value       TEXT,
            reason          TEXT,
            changed_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def complexity_label(points):
    """Convert story points to complexity label."""
    if points <= 2:   return "LOW"
    elif points <= 5: return "MEDIUM"
    elif points <= 8: return "HIGH"
    else:             return "VERY HIGH"


def load_sprint_data():
    """
    Load sprint plan from JSON file (written by Streamlit app)
    or from SQLite database as fallback.
    """
    # Try JSON file first (most up to date from Streamlit)
    if os.path.exists(OUTPUT_JSON):
        try:
            df = pd.read_json(OUTPUT_JSON)
            if not df.empty:
                tasks = []
                for _, row in df.iterrows():
                    tasks.append({
                        "task_id":                str(row.get("story_id", "")),
                        "title":                  str(row.get("title", "")),
                        "sprint_number":          int(row.get("sprint_number", 1)),
                        "priority":               str(row.get("priority", "LOW")),
                        "priority_confidence_pct":float(row.get("priority_confidence_pct", 0)),
                        "story_points":           int(row.get("story_points", 0)),
                        "complexity":             complexity_label(int(row.get("story_points", 0))),
                        "estimated_hours":        int(row.get("estimated_hours", 0)),
                        "sprint_length_days":     int(row.get("sprint_length_days", 14)),
                        "team_size":              int(row.get("team_size", 5)),
                    })
                return tasks
        except Exception:
            pass

    # Fallback to SQLite
    try:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM sprint_plans ORDER BY sprint_number, story_points DESC"
        ).fetchall()
        conn.close()
        tasks = []
        for row in rows:
            row = dict(row)
            tasks.append({
                "task_id":                str(row.get("story_id", "")),
                "title":                  str(row.get("title", "")),
                "sprint_number":          int(row.get("sprint_number", 1)),
                "priority":               str(row.get("priority", "LOW")),
                "priority_confidence_pct":0.0,
                "story_points":           int(row.get("story_points", 0)),
                "complexity":             complexity_label(int(row.get("story_points", 0))),
                "estimated_hours":        int(row.get("estimated_hours", 0)),
                "sprint_length_days":     int(row.get("sprint_length", 14)),
                "team_size":              int(row.get("team_size", 5)),
            })
        return tasks
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

# ── Health Check ──────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    """
    Check if the API is running.

    Response:
        {
            "status": "ok",
            "message": "Sprint Planning API is running",
            "models_loaded": true,
            "sprint_plan_ready": true,
            "endpoints": [...]
        }
    """
    tasks          = load_sprint_data()
    plan_ready     = len(tasks) > 0

    return jsonify({
        "status":           "ok",
        "message":          "Sprint Planning API — Member 2 (IT22134844)",
        "models_loaded":    MODELS_LOADED,
        "sprint_plan_ready":plan_ready,
        "total_tasks":      len(tasks),
        "endpoints": [
            "GET  /api/health",
            "GET  /api/sprint-plan",
            "GET  /api/sprint-plan/<sprint_number>",
            "GET  /api/stories",
            "POST /api/predict-priority",
            "POST /api/replan",
        ]
    }), 200


# ── GET All Sprint Plan ───────────────────────────────────
@app.route("/api/sprint-plan", methods=["GET"])
def get_sprint_plan():
    """
    Get the full sprint plan with all tasks across all sprints.
    Member 3 calls this to get the complete list of tasks
    for resource allocation.

    Response:
        {
            "status": "success",
            "generated_at": "2026-04-21 09:35:00",
            "total_tasks": 10,
            "total_sprints": 2,
            "tasks": [
                {
                    "task_id": "US001",
                    "title": "Fix security vulnerability",
                    "sprint_number": 1,
                    "priority": "HIGH",
                    "priority_confidence_pct": 87.3,
                    "story_points": 8,
                    "complexity": "HIGH",
                    "estimated_hours": 64,
                    "sprint_length_days": 14,
                    "team_size": 5
                },
                ...
            ]
        }
    """
    tasks = load_sprint_data()

    if not tasks:
        return jsonify({
            "status":  "error",
            "message": "No sprint plan found. Please generate a sprint plan from the Streamlit app first.",
            "hint":    "Run the Streamlit app, add user stories, and click Generate Sprint Plan."
        }), 404

    total_sprints = max(t["sprint_number"] for t in tasks) if tasks else 0

    return jsonify({
        "status":        "success",
        "generated_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tasks":   len(tasks),
        "total_sprints": total_sprints,
        "tasks":         tasks
    }), 200


# ── GET Sprint by Number ──────────────────────────────────
@app.route("/api/sprint-plan/<int:sprint_number>", methods=["GET"])
def get_sprint_by_number(sprint_number):
    """
    Get tasks for a specific sprint number only.
    Useful when Member 3 wants to allocate resources
    one sprint at a time.

    URL Parameter:
        sprint_number (int): The sprint number e.g. 1, 2, 3

    Response:
        {
            "status": "success",
            "sprint_number": 1,
            "total_tasks": 5,
            "total_story_points": 28,
            "tasks": [ ... ]
        }
    """
    all_tasks = load_sprint_data()

    if not all_tasks:
        return jsonify({
            "status":  "error",
            "message": "No sprint plan found."
        }), 404

    sprint_tasks = [t for t in all_tasks if t["sprint_number"] == sprint_number]

    if not sprint_tasks:
        available = sorted(set(t["sprint_number"] for t in all_tasks))
        return jsonify({
            "status":           "error",
            "message":          f"Sprint {sprint_number} not found.",
            "available_sprints": available
        }), 404

    total_points = sum(t["story_points"] for t in sprint_tasks)
    total_hours  = sum(t["estimated_hours"] for t in sprint_tasks)

    return jsonify({
        "status":             "success",
        "sprint_number":      sprint_number,
        "total_tasks":        len(sprint_tasks),
        "total_story_points": total_points,
        "total_hours":        total_hours,
        "tasks":              sprint_tasks
    }), 200


# ── GET All Stories ───────────────────────────────────────
@app.route("/api/stories", methods=["GET"])
def get_stories():
    """
    Get all user stories with their predicted priorities.
    Returns stories before sprint allocation — useful for
    Member 3 to understand the full backlog.

    Response:
        {
            "status": "success",
            "total": 10,
            "stories": [ ... ]
        }
    """
    try:
        conn  = get_db()
        rows  = conn.execute(
            "SELECT * FROM user_stories ORDER BY priority DESC, story_points DESC"
        ).fetchall()
        conn.close()

        stories = [dict(row) for row in rows]

        if not stories:
            return jsonify({
                "status":  "error",
                "message": "No user stories found in database."
            }), 404

        return jsonify({
            "status":  "success",
            "total":   len(stories),
            "stories": stories
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ── POST Predict Priority ─────────────────────────────────
@app.route("/api/predict-priority", methods=["POST"])
def predict_priority():
    """
    Predict the priority of a user story using the ML model.
    Member 3 can use this to check priority of new tasks.

    Request Body (JSON):
        {
            "title": "Fix critical login bug",
            "description": "Users cannot log in due to session error"
        }

    Response:
        {
            "status": "success",
            "title": "Fix critical login bug",
            "priority": "HIGH",
            "confidence": 89.4
        }
    """
    if not MODELS_LOADED:
        return jsonify({
            "status":  "error",
            "message": "ML models not loaded on server."
        }), 503

    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({
            "status":  "error",
            "message": "Request body must contain at least a 'title' field.",
            "example": {
                "title":       "Fix critical login bug",
                "description": "Users cannot log in due to session error"
            }
        }), 400

    title       = str(data.get("title", ""))
    description = str(data.get("description", ""))
    full_text   = title + " " + description

    try:
        features   = tfidf.transform([full_text])
        pred       = priority_model.predict(features)[0]
        proba      = priority_model.predict_proba(features)[0]
        priority   = "HIGH" if pred == 1 else "LOW"
        confidence = round(float(max(proba)) * 100, 1)

        return jsonify({
            "status":     "success",
            "title":      title,
            "priority":   priority,
            "confidence": confidence,
            "model":      "Random Forest + TF-IDF (Accuracy: 67.58%)"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ── POST Re-plan (scope change from Member 4) ─────────────
@app.route("/api/replan", methods=["POST"])
def trigger_replan():
    """
    Trigger a re-planning event. This endpoint is called when
    a scope change needs to be recorded. It logs the change
    and returns the updated sprint plan.

    Request Body (JSON):
        {
            "change_type": "NEW_STORY_ADDED",
            "story_id":    "US011",
            "reason":      "Production issue found",
            "new_value":   "Critical database crash"
        }

    Change types:
        NEW_STORY_ADDED
        STORY_REMOVED
        STORY_MODIFIED
        PRIORITY_CHANGED

    Response:
        {
            "status": "success",
            "message": "Change logged successfully",
            "change_logged": { ... },
            "updated_sprint_plan": [ ... ]
        }
    """
    data = request.get_json()

    if not data or "change_type" not in data:
        return jsonify({
            "status":  "error",
            "message": "Request body must contain 'change_type'.",
            "valid_change_types": [
                "NEW_STORY_ADDED",
                "STORY_REMOVED",
                "STORY_MODIFIED",
                "PRIORITY_CHANGED"
            ]
        }), 400

    change_type = data.get("change_type", "")
    story_id    = data.get("story_id", "")
    old_value   = data.get("old_value", "")
    new_value   = data.get("new_value", "")
    reason      = data.get("reason", "")

    valid_types = ["NEW_STORY_ADDED", "STORY_REMOVED", "STORY_MODIFIED", "PRIORITY_CHANGED"]
    if change_type not in valid_types:
        return jsonify({
            "status":  "error",
            "message": f"Invalid change_type. Must be one of: {valid_types}"
        }), 400

    try:
        # Log change to database
        conn = get_db()
        conn.execute("""
            INSERT INTO change_logs
            (change_type, story_id, old_value, new_value, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (change_type, story_id, old_value, new_value, reason))
        conn.commit()
        conn.close()

        # Return updated sprint plan
        tasks = load_sprint_data()

        return jsonify({
            "status":  "success",
            "message": "Change logged. Please regenerate the sprint plan in the Streamlit app.",
            "change_logged": {
                "change_type": change_type,
                "story_id":    story_id,
                "reason":      reason,
                "logged_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "current_sprint_plan_task_count": len(tasks)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ── 404 handler ───────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status":  "error",
        "message": "Endpoint not found.",
        "available_endpoints": [
            "GET  /api/health",
            "GET  /api/sprint-plan",
            "GET  /api/sprint-plan/<sprint_number>",
            "GET  /api/stories",
            "POST /api/predict-priority",
            "POST /api/replan",
        ]
    }), 404


# ── 500 handler ───────────────────────────────────────────
@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "status":  "error",
        "message": "Internal server error.",
        "detail":  str(e)
    }), 500


# ── Run ───────────────────────────────────────────────────
@app.route("/api/replan-full", methods=["POST"])
def replan_full():
    """
    Full re-planning endpoint.
    Adds, removes, or modifies a story and regenerates
    the sprint plan automatically.

    Request Body:
    {
        "change_type": "NEW_STORY_ADDED",
        "story_id":    "US011",
        "title":       "Critical database crash",
        "description": "Database crashes for all users",
        "story_points": 13,
        "urgency":     "CRITICAL",
        "reason":      "Production issue"
    }
    """
    data = request.get_json()

    if not data or "change_type" not in data:
        return jsonify({"status": "error", "message": "change_type required"}), 400

    change_type  = data.get("change_type", "")
    story_id     = data.get("story_id", "")
    title        = data.get("title", "")
    description  = data.get("description", "")
    story_points = int(data.get("story_points", 5))
    reason       = data.get("reason", "")
    urgency      = data.get("urgency", "MEDIUM")

    try:
        # Load current stories from database
        conn    = get_db()
        rows    = conn.execute("SELECT * FROM user_stories").fetchall()
        stories = [dict(r) for r in rows]
        conn.close()

        # Apply the change
        if change_type == "NEW_STORY_ADDED":
            existing_ids = [s["story_id"] for s in stories]
            if story_id in existing_ids:
                return jsonify({
                    "status":  "error",
                    "message": f"Story {story_id} already exists."
                }), 400

            # Predict priority using ML model
            if MODELS_LOADED:
                full_text  = title + " " + description
                features   = tfidf.transform([full_text])
                pred       = priority_model.predict(features)[0]
                proba      = priority_model.predict_proba(features)[0]
                priority   = "HIGH" if pred == 1 else "LOW"
                confidence = round(float(max(proba)) * 100, 1)
            else:
                priority   = "HIGH" if urgency in ["CRITICAL", "HIGH"] else "LOW"
                confidence = 75.0

            new_story = {
                "story_id":    story_id,
                "title":       title,
                "description": description,
                "story_points":story_points,
                "priority":    priority,
                "confidence":  confidence,
            }
            stories.append(new_story)

        elif change_type == "STORY_REMOVED":
            stories = [s for s in stories if s["story_id"] != story_id]

        elif change_type == "STORY_MODIFIED":
            for s in stories:
                if s["story_id"] == story_id:
                    s["story_points"] = story_points
                    if title:
                        s["title"] = title
                    break

        elif change_type == "PRIORITY_CHANGED":
            for s in stories:
                if s["story_id"] == story_id:
                    s["priority"] = "HIGH" if urgency in ["CRITICAL","HIGH"] else "LOW"
                    break

        # Save updated stories to database
        conn = get_db()
        conn.execute("DELETE FROM user_stories")
        for s in stories:
            conn.execute("""
                INSERT OR REPLACE INTO user_stories
                (story_id, title, description, story_points, priority, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                s["story_id"], s["title"], s.get("description",""),
                s["story_points"], s["priority"], s.get("confidence", 0)
            ))
        conn.commit()
        conn.close()

        # Re-run sprint allocation (Greedy Bin Packing)
        sprint_capacity = 30
        urgency_val = data.get("urgency", "MEDIUM")

        def sort_key(x):
            # CRITICAL new story always goes first
            if x["story_id"] == story_id and urgency_val == "CRITICAL":
                return (0, 0, x["story_points"])
            # Then all HIGH priority
            if x["priority"] == "HIGH":
                return (0, 1, x["story_points"])
            # Then LOW priority
            return (1, 1, x["story_points"])

        stories_sorted = sorted(stories, key=sort_key)
        sprints       = {}
        current_sprint = 1
        current_load   = 0

        for story in stories_sorted:
            pts = story["story_points"]
            if current_load + pts <= sprint_capacity:
                if current_sprint not in sprints:
                    sprints[current_sprint] = []
                sprints[current_sprint].append(story)
                current_load += pts
            else:
                current_sprint += 1
                current_load    = pts
                if current_sprint not in sprints:
                    sprints[current_sprint] = []
                sprints[current_sprint].append(story)

        # Save new sprint plan to database
        conn = get_db()
        conn.execute("DELETE FROM sprint_plans")
        for sprint_num, sprint_stories in sprints.items():
            for s in sprint_stories:
                conn.execute("""
                    INSERT INTO sprint_plans
                    (sprint_number, story_id, title, priority,
                     story_points, estimated_hours, sprint_length, team_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sprint_num, s["story_id"], s["title"], s["priority"],
                    s["story_points"], s["story_points"] * 8, 14, 5
                ))

        # Log the change
        conn.execute("""
            INSERT INTO change_logs
            (change_type, story_id, old_value, new_value, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (change_type, story_id, "", title, reason))
        conn.commit()
        conn.close()

        # Build output for member 3
        output_tasks = []
        for sprint_num, sprint_stories in sprints.items():
            for s in sprint_stories:
                output_tasks.append({
                    "story_id":                s["story_id"],
                    "title":                   s["title"],
                    "sprint_number":           sprint_num,
                    "priority":                s["priority"],
                    "priority_confidence_pct": s.get("confidence", 0),
                    "story_points":            s["story_points"],
                    "estimated_hours":         s["story_points"] * 8,
                    "sprint_length_days":      14,
                    "team_size":               5,
                })

        # Save output JSON for member 3
        import json as json_module
        with open(OUTPUT_JSON, "w") as f:
            json_module.dump(output_tasks, f, indent=2)

        total_sprints = max(sprints.keys()) if sprints else 0

        return jsonify({
            "status":         "success",
            "message":        f"Change applied and sprint plan regenerated.",
            "change_type":    change_type,
            "story_id":       story_id,
            "total_tasks":    len(stories),
            "total_sprints":  total_sprints,
            "tasks": [{
                "task_id":       s["story_id"],
                "title":         s["title"],
                "sprint_number": n,
                "priority":      s["priority"],
                "priority_confidence_pct": s.get("confidence", 0),
                "story_points":  s["story_points"],
                "complexity":    complexity_label(s["story_points"]),
                "estimated_hours": s["story_points"] * 8,
                "sprint_length_days": 14,
                "team_size": 5,
            } for n, ss in sprints.items() for s in ss]
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
if __name__ == "__main__":
    print("=" * 55)
    print("  Sprint Planning API — Member 2 (IT22134844)")
    print("=" * 55)
    init_db()
    print("✅ Database initialised")
    print("🚀 Starting API on http://localhost:5000")
    print()
    print("  Available endpoints:")
    print("  GET  http://localhost:5000/api/health")
    print("  GET  http://localhost:5000/api/sprint-plan")
    print("  GET  http://localhost:5000/api/sprint-plan/1")
    print("  GET  http://localhost:5000/api/stories")
    print("  POST http://localhost:5000/api/predict-priority")
    print("  POST http://localhost:5000/api/replan")
    print("=" * 55)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=8080)
