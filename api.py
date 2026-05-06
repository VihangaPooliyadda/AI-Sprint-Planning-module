"""
============================================================
  SPRINT PLANNING API — Member 2: T.M.V.M.B. Pooliyadda
  IT22134844 | R26-ISE-005

  Base URL : http://localhost:8080

  ENDPOINTS:
    GET  /api/health
    GET  /api/sprint-plan
    GET  /api/sprint-plan/<sprint_number>
    GET  /api/stories
    POST /api/sprint-plan
    POST /api/predict-priority
    POST /api/replan
    POST /api/replan-full
    POST /api/upload-sprint-plan
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

# ── App setup ──────────────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Paths ──────────────────────────────────────────────────
BASE        = os.path.dirname(os.path.abspath(__file__))
MODEL_PKL   = os.path.join(BASE, "priority_model.pkl")
TFIDF_PKL   = os.path.join(BASE, "priority_tfidf.pkl")
EFFORT_PKL  = os.path.join(BASE, "effort_model.pkl")
OUTPUT_JSON = os.path.join(BASE, "output_for_member3.json")

if os.name == "nt":
    DB_PATH = os.path.join(BASE, "sprint_planning.db")
else:
    DB_PATH = os.path.join("/tmp", "sprint_planning.db")

# ── Download models if not present ────────────────────────
def download_models():
    if os.path.exists(MODEL_PKL) and os.path.exists(TFIDF_PKL):
        print("✅ Models found locally — skipping download")
        return True
    try:
        import gdown
        if not os.path.exists(MODEL_PKL):
            print("⬇️  Downloading priority model...")
            gdown.download(
                f"https://drive.google.com/uc?id={os.environ.get('PRIORITY_MODEL_ID','')}",
                MODEL_PKL, quiet=False)
            print("✅ Priority model downloaded")
        if not os.path.exists(TFIDF_PKL):
            print("⬇️  Downloading TF-IDF model...")
            gdown.download(
                f"https://drive.google.com/uc?id={os.environ.get('TFIDF_ID','')}",
                TFIDF_PKL, quiet=False)
            print("✅ TF-IDF model downloaded")
        if not os.path.exists(EFFORT_PKL):
            print("⬇️  Downloading effort model...")
            gdown.download(
                f"https://drive.google.com/uc?id={os.environ.get('EFFORT_MODEL_ID','')}",
                EFFORT_PKL, quiet=False)
            print("✅ Effort model downloaded")
        return True
    except ImportError:
        print("⚠️  gdown not installed — skipping download")
        return False
    except Exception as e:
        print(f"⚠️  Download failed: {e}")
        return False

# ── Load ML models ─────────────────────────────────────────
try:
    download_models()
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
    if points <= 2:   return "LOW"
    elif points <= 5: return "MEDIUM"
    elif points <= 8: return "HIGH"
    else:             return "VERY HIGH"

def load_sprint_data():
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
    try:
        init_db()
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

def run_greedy_bin_packing(stories, sprint_capacity=30):
    stories_sorted = sorted(
        stories,
        key=lambda x: (0 if x.get("priority") == "HIGH" else 1, x.get("story_points", 0))
    )
    sprints        = {}
    current_sprint = 1
    current_load   = 0
    for story in stories_sorted:
        pts = story.get("story_points", 0)
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
    return sprints

# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.route("/api/health", methods=["GET"])
def health():
    tasks      = load_sprint_data()
    plan_ready = len(tasks) > 0
    return jsonify({
        "status":            "ok",
        "message":           "Sprint Planning API — Member 2 (IT22134844)",
        "models_loaded":     MODELS_LOADED,
        "sprint_plan_ready": plan_ready,
        "total_tasks":       len(tasks),
        "endpoints": [
            "GET  /api/health",
            "GET  /api/sprint-plan",
            "GET  /api/sprint-plan/<sprint_number>",
            "GET  /api/stories",
            "POST /api/sprint-plan",
            "POST /api/predict-priority",
            "POST /api/replan",
            "POST /api/replan-full",
            "POST /api/upload-sprint-plan",
        ]
    }), 200

@app.route("/api/sprint-plan", methods=["GET"])
def get_sprint_plan():
    tasks = load_sprint_data()
    if not tasks:
        return jsonify({
            "status":  "error",
            "message": "No sprint plan found. Please generate a sprint plan first.",
            "hint":    "Add stories and click Generate Sprint Plan."
        }), 404
    total_sprints = max(t["sprint_number"] for t in tasks) if tasks else 0
    return jsonify({
        "status":        "success",
        "generated_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tasks":   len(tasks),
        "total_sprints": total_sprints,
        "tasks":         tasks
    }), 200

@app.route("/api/sprint-plan", methods=["POST"])
def post_sprint_plan():
    try:
        init_db()
        data            = request.get_json()
        stories         = data.get("stories",         [])
        sprint_capacity = int(data.get("sprint_capacity", 30))
        sprint_length   = int(data.get("sprint_length",   14))
        team_size       = int(data.get("team_size",         5))

        if not stories:
            return jsonify({"status": "error", "message": "No stories provided"}), 400

        conn = get_db()
        conn.execute("DELETE FROM user_stories")
        for s in stories:
            conn.execute("""
                INSERT OR REPLACE INTO user_stories
                (story_id, title, description, story_points, priority, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (s.get("story_id",""), s.get("title",""), s.get("description",""),
                  s.get("story_points",0), s.get("priority","LOW"), s.get("confidence",0)))
        conn.commit()
        conn.close()

        sprints = run_greedy_bin_packing(stories, sprint_capacity)

        conn = get_db()
        conn.execute("DELETE FROM sprint_plans")
        for sprint_num, sprint_stories in sprints.items():
            for s in sprint_stories:
                conn.execute("""
                    INSERT INTO sprint_plans
                    (sprint_number, story_id, title, priority,
                     story_points, estimated_hours, sprint_length, team_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (sprint_num, s.get("story_id",""), s.get("title",""),
                      s.get("priority","LOW"), s.get("story_points",0),
                      s.get("story_points",0)*8, sprint_length, team_size))
        conn.commit()
        conn.close()

        output_tasks = []
        for sprint_num, sprint_stories in sprints.items():
            for s in sprint_stories:
                output_tasks.append({
                    "story_id":                s.get("story_id",""),
                    "title":                   s.get("title",""),
                    "sprint_number":           sprint_num,
                    "priority":                s.get("priority","LOW"),
                    "priority_confidence_pct": s.get("confidence",0),
                    "story_points":            s.get("story_points",0),
                    "estimated_hours":         s.get("story_points",0)*8,
                    "sprint_length_days":      sprint_length,
                    "team_size":               team_size,
                })

        with open(OUTPUT_JSON, "w") as f:
            json.dump(output_tasks, f, indent=2)

        total_sprints = max(sprints.keys()) if sprints else 0

        return jsonify({
            "status":        "success",
            "message":       "Sprint plan generated and saved successfully",
            "total_stories": len(stories),
            "total_sprints": total_sprints,
            "tasks": [{
                "task_id":                 s.get("story_id",""),
                "title":                   s.get("title",""),
                "sprint_number":           n,
                "priority":                s.get("priority","LOW"),
                "priority_confidence_pct": s.get("confidence",0),
                "story_points":            s.get("story_points",0),
                "complexity":              complexity_label(s.get("story_points",0)),
                "estimated_hours":         s.get("story_points",0)*8,
                "sprint_length_days":      sprint_length,
                "team_size":               team_size,
            } for n, ss in sprints.items() for s in ss]
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/sprint-plan/<int:sprint_number>", methods=["GET"])
def get_sprint_by_number(sprint_number):
    all_tasks = load_sprint_data()
    if not all_tasks:
        return jsonify({"status": "error", "message": "No sprint plan found."}), 404
    sprint_tasks = [t for t in all_tasks if t["sprint_number"] == sprint_number]
    if not sprint_tasks:
        available = sorted(set(t["sprint_number"] for t in all_tasks))
        return jsonify({
            "status":            "error",
            "message":           f"Sprint {sprint_number} not found.",
            "available_sprints": available
        }), 404
    return jsonify({
        "status":             "success",
        "sprint_number":      sprint_number,
        "total_tasks":        len(sprint_tasks),
        "total_story_points": sum(t["story_points"] for t in sprint_tasks),
        "total_hours":        sum(t["estimated_hours"] for t in sprint_tasks),
        "tasks":              sprint_tasks
    }), 200

@app.route("/api/stories", methods=["GET"])
def get_stories():
    try:
        init_db()
        conn  = get_db()
        rows  = conn.execute(
            "SELECT * FROM user_stories ORDER BY priority DESC, story_points DESC"
        ).fetchall()
        conn.close()
        stories = [dict(row) for row in rows]
        if not stories:
            return jsonify({"status": "error", "message": "No user stories found."}), 404
        return jsonify({"status": "success", "total": len(stories), "stories": stories}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/predict-priority", methods=["POST"])
def predict_priority():
    if not MODELS_LOADED:
        return jsonify({"status": "error", "message": "ML models not loaded."}), 503
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"status": "error", "message": "Please provide a title field."}), 400
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

@app.route("/api/replan", methods=["POST"])
def trigger_replan():
    data = request.get_json()
    if not data or "change_type" not in data:
        return jsonify({"status": "error", "message": "change_type required."}), 400
    change_type = data.get("change_type", "")
    story_id    = data.get("story_id",    "")
    old_value   = data.get("old_value",   "")
    new_value   = data.get("new_value",   "")
    reason      = data.get("reason",      "")
    valid_types = ["NEW_STORY_ADDED","STORY_REMOVED","STORY_MODIFIED","PRIORITY_CHANGED"]
    if change_type not in valid_types:
        return jsonify({"status": "error",
            "message": f"Invalid change_type. Must be one of: {valid_types}"}), 400
    try:
        init_db()
        conn = get_db()
        conn.execute("""
            INSERT INTO change_logs (change_type, story_id, old_value, new_value, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (change_type, story_id