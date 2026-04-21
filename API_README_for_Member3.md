# Sprint Planning API — Member 2
## T.M.V.M.B. Pooliyadda | IT22134844 | R26-ISE-005

This API provides sprint plan data from the **Sprint Planning and Allocation Component (Member 2)**
for use by the **Resource Allocation Component (Member 3)**.

---

## Setup Instructions

### Step 1 — Install required libraries

```
pip install flask flask-cors pandas
```

### Step 2 — Place the file

Put `api.py` in the same folder as the Sprint Planning project:
```
C:/Users/lap.lk/Desktop/Research 4.1/api.py
```

### Step 3 — Make sure the sprint plan exists

1. Run the Streamlit app first
2. Add user stories
3. Click **Generate Sprint Plan**
4. This creates `output_for_member3.json` which the API reads from

### Step 4 — Start the API

```
python api.py
```

The API will start at: **http://localhost:5000**

---

## Base URL

```
http://localhost:5000
```

---

## Endpoints

---

### 1. Health Check
Check if the API is running and ready.

```
GET /api/health
```

**Example Response:**
```json
{
    "status": "ok",
    "message": "Sprint Planning API — Member 2 (IT22134844)",
    "models_loaded": true,
    "sprint_plan_ready": true,
    "total_tasks": 10,
    "endpoints": [
        "GET  /api/health",
        "GET  /api/sprint-plan",
        "GET  /api/sprint-plan/<sprint_number>",
        "GET  /api/stories",
        "POST /api/predict-priority",
        "POST /api/replan"
    ]
}
```

---

### 2. Get Full Sprint Plan ⭐ MAIN ENDPOINT
Get all tasks across all sprints. **This is the main endpoint Member 3 should call.**

```
GET /api/sprint-plan
```

**Example Response:**
```json
{
    "status": "success",
    "generated_at": "2026-04-21 09:35:00",
    "total_tasks": 10,
    "total_sprints": 2,
    "tasks": [
        {
            "task_id": "US001",
            "title": "Fix critical security vulnerability in login system",
            "sprint_number": 1,
            "priority": "HIGH",
            "priority_confidence_pct": 87.3,
            "story_points": 8,
            "complexity": "HIGH",
            "estimated_hours": 64,
            "sprint_length_days": 14,
            "team_size": 5
        },
        {
            "task_id": "US002",
            "title": "Add export to PDF feature",
            "sprint_number": 1,
            "priority": "LOW",
            "priority_confidence_pct": 72.1,
            "story_points": 5,
            "complexity": "MEDIUM",
            "estimated_hours": 40,
            "sprint_length_days": 14,
            "team_size": 5
        }
    ]
}
```

**Field Descriptions:**

| Field | Type | Description |
|---|---|---|
| task_id | string | Unique story identifier |
| title | string | Story title |
| sprint_number | integer | Which sprint this task belongs to |
| priority | string | HIGH or LOW (ML predicted) |
| priority_confidence_pct | float | Model confidence percentage (0-100) |
| story_points | integer | Effort in story points |
| complexity | string | LOW / MEDIUM / HIGH / VERY HIGH |
| estimated_hours | integer | Estimated hours (story_points x 8) |
| sprint_length_days | integer | Sprint duration in days |
| team_size | integer | Number of developers in team |

---

### 3. Get Tasks for a Specific Sprint
Get tasks for one sprint at a time.

```
GET /api/sprint-plan/<sprint_number>
```

**Example:**
```
GET /api/sprint-plan/1
```

**Example Response:**
```json
{
    "status": "success",
    "sprint_number": 1,
    "total_tasks": 5,
    "total_story_points": 28,
    "total_hours": 224,
    "tasks": [ ... ]
}
```

---

### 4. Get All User Stories
Get all user stories before sprint allocation.

```
GET /api/stories
```

**Example Response:**
```json
{
    "status": "success",
    "total": 10,
    "stories": [
        {
            "story_id": "US001",
            "title": "Fix critical security vulnerability",
            "description": "Users can bypass authentication...",
            "story_points": 8,
            "priority": "HIGH",
            "confidence": 87.3
        }
    ]
}
```

---

### 5. Predict Priority for a Story
Send a user story and get back a priority prediction from the ML model.

```
POST /api/predict-priority
Content-Type: application/json
```

**Request Body:**
```json
{
    "title": "Fix critical login bug",
    "description": "Users cannot log in due to session error affecting all users"
}
```

**Example Response:**
```json
{
    "status": "success",
    "title": "Fix critical login bug",
    "priority": "HIGH",
    "confidence": 89.4,
    "model": "Random Forest + TF-IDF (Accuracy: 67.58%)"
}
```

---

### 6. Log a Re-planning Event
Log a scope change event to the database.

```
POST /api/replan
Content-Type: application/json
```

**Request Body:**
```json
{
    "change_type": "NEW_STORY_ADDED",
    "story_id": "US011",
    "reason": "Critical production issue discovered",
    "new_value": "Database crash affecting all users"
}
```

**Valid change_type values:**
- `NEW_STORY_ADDED`
- `STORY_REMOVED`
- `STORY_MODIFIED`
- `PRIORITY_CHANGED`

**Example Response:**
```json
{
    "status": "success",
    "message": "Change logged. Please regenerate the sprint plan in the Streamlit app.",
    "change_logged": {
        "change_type": "NEW_STORY_ADDED",
        "story_id": "US011",
        "reason": "Critical production issue discovered",
        "logged_at": "2026-04-21 09:35:00"
    }
}
```

---

## How to Call From Your System

### Using Python (requests library)

```python
import requests

# Get full sprint plan
response = requests.get("http://localhost:5000/api/sprint-plan")
data = response.json()

if data["status"] == "success":
    tasks = data["tasks"]
    for task in tasks:
        print(f"Task: {task['task_id']} | Sprint: {task['sprint_number']} | Priority: {task['priority']} | Hours: {task['estimated_hours']}")
```

### Using JavaScript (fetch)

```javascript
fetch("http://localhost:5000/api/sprint-plan")
  .then(res => res.json())
  .then(data => {
    if (data.status === "success") {
      data.tasks.forEach(task => {
        console.log(task.task_id, task.priority, task.estimated_hours);
      });
    }
  });
```

### Using Axios

```javascript
const axios = require("axios");

const response = await axios.get("http://localhost:5000/api/sprint-plan");
const tasks = response.data.tasks;
```

---

## Integration Flow

```
Member 1                Member 2 (Me)               Member 3 (You)
────────                ─────────────               ──────────────
User Stories    →   Priority Prediction         
                    Effort Estimation           
                    Sprint Allocation           →  GET /api/sprint-plan
                    output_for_member3.json     →  Use tasks[] for
                                                   your AI allocation
Member 4                                            /ai/allocate API
────────
Change Alert    →   Re-planning Module
                    POST /api/replan
```

---

## Error Responses

All errors follow this format:

```json
{
    "status": "error",
    "message": "Description of what went wrong"
}
```

| HTTP Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request — check your request body |
| 404 | Not found — sprint plan may not exist yet |
| 500 | Server error |
| 503 | ML models not loaded |

---

## Contact

**Member 2:** T.M.V.M.B. Pooliyadda
**Student ID:** IT22134844
**Project ID:** R26-ISE-005
**GitHub:** https://github.com/VihangaPooliyadda/AI-Sprint-Planning-module
