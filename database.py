import sqlite3
import os

BASE    = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1")
DB_PATH = os.path.join(BASE, "sprint_planning.db")

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

        CREATE TABLE IF NOT EXISTS model_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name      TEXT,
            accuracy        REAL,
            f1_score        REAL,
            mae             REAL,
            r2_score        REAL,
            logged_at       DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("✅ Database created at:", DB_PATH)
    print("✅ Tables created: user_stories, sprint_plans, change_logs, model_logs")

def save_stories(stories):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_stories")
    for s in stories:
        cursor.execute("""
            INSERT OR REPLACE INTO user_stories
            (story_id, title, description, story_points, priority, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            s["story_id"], s["title"], s.get("description", ""),
            s["story_points"], s["priority"], s.get("confidence", 0)
        ))
    conn.commit()
    conn.close()

def load_stories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_stories ORDER BY priority DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_sprint_plan(sprint_plan, sprint_length=14, team_size=5):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sprint_plans")
    for sprint_num, stories in sprint_plan.items():
        for s in stories:
            cursor.execute("""
                INSERT INTO sprint_plans
                (sprint_number, story_id, title, priority,
                 story_points, estimated_hours, sprint_length, team_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sprint_num, s["story_id"], s["title"], s["priority"],
                s["story_points"], s["story_points"] * 8,
                sprint_length, team_size
            ))
    conn.commit()
    conn.close()

def load_sprint_plan():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sprint_plans ORDER BY sprint_number")
    rows = cursor.fetchall()
    conn.close()
    plan = {}
    for row in rows:
        row = dict(row)
        num = row["sprint_number"]
        if num not in plan:
            plan[num] = []
        plan[num].append(row)
    return plan

def log_change(change_type, story_id, old_value="", new_value="", reason=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO change_logs
        (change_type, story_id, old_value, new_value, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (change_type, story_id, old_value, new_value, reason))
    conn.commit()
    conn.close()

def load_change_history():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM change_logs ORDER BY changed_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()