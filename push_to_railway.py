"""
Run this script after generating a sprint plan in Streamlit.
It pushes your local sprint plan to the Railway server
so Member 3 can access it from anywhere.
"""

import requests
import json
import os

# ── Change this to your Railway URL ──────────────────────
RAILWAY_URL = "web-production-ecda6.up.railway.app"

# ── Local sprint plan file ────────────────────────────────
LOCAL_JSON = os.path.join(
    "C:", os.sep, "Users", "lap.lk",
    "Desktop", "Research 4.1",
    "output_for_member3.json"
)

def push_sprint_plan():
    print("=" * 50)
    print("  Pushing Sprint Plan to Railway Server")
    print("=" * 50)

    # Check if local file exists
    if not os.path.exists(LOCAL_JSON):
        print("❌ output_for_member3.json not found!")
        print("   Please generate a sprint plan in Streamlit first.")
        return

    # Load local sprint plan
    with open(LOCAL_JSON) as f:
        tasks = json.load(f)

    if not tasks:
        print("❌ Sprint plan is empty!")
        print("   Please generate a sprint plan in Streamlit first.")
        return

    print(f"✅ Found {len(tasks)} tasks locally")
    print(f"🚀 Pushing to {RAILWAY_URL}...")

    # Send to Railway
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/upload-sprint-plan",
            json={"tasks": tasks},
            timeout=30
        )
        data = response.json()

        if data.get("status") == "success":
            print(f"✅ Successfully uploaded {data['total_tasks']} tasks to Railway!")
            print(f"🌐 Member 3 can now access: {RAILWAY_URL}/api/sprint-plan")
        else:
            print(f"❌ Upload failed: {data.get('message')}")

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {RAILWAY_URL}")
        print("   Check your Railway URL is correct.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    push_sprint_plan()