import pandas as pd
import os

print("=" * 60)
print("OUTPUT GENERATOR — FOR MEMBER 3 (Resource Allocation)")
print("=" * 60)

base = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1")

# Load the sprint plan
# Use updated plan if it exists, otherwise use original
updated_path = os.path.join(base, "sprint_plan_updated.csv")
original_path = os.path.join(base, "sprint_plan_output.csv")

if os.path.exists(updated_path):
    df = pd.read_csv(updated_path)
    print("Using updated sprint plan (after re-planning)")
else:
    df = pd.read_csv(original_path)
    print("Using original sprint plan")

# ============================================
print("\n[STEP 1] SPRINT SUMMARY FOR MEMBER 3...")
# ============================================

print("\n" + "=" * 60)
print("SPRINT PLAN HANDOFF TO MEMBER 3")
print("=" * 60)

SPRINT_CAPACITY = 30
SPRINT_LENGTH   = 14
NUM_DEVELOPERS  = 5

for sprint_num in sorted(df["sprint_number"].unique()):
    sprint_df = df[df["sprint_number"] == sprint_num]
    total_pts  = sprint_df["story_points"].sum()
    high_count = (sprint_df["priority"] == "HIGH").sum()
    low_count  = (sprint_df["priority"] == "LOW").sum()
    capacity   = round(total_pts / SPRINT_CAPACITY * 100)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SPRINT {sprint_num}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Duration        : {SPRINT_LENGTH} days
 Team Size       : {NUM_DEVELOPERS} developers
 Total Points    : {total_pts} / {SPRINT_CAPACITY}
 Capacity Used   : {capacity}%
 HIGH Priority   : {high_count} stories
 LOW Priority    : {low_count} stories
""")

    print(f" {'Story ID':<8} {'Priority':<8} {'Points':<8} Title")
    print(f" {'-'*8} {'-'*8} {'-'*8} {'-'*35}")

    for _, row in sprint_df.iterrows():
        icon = "🔴" if row["priority"] == "HIGH" else "🟢"
        print(f" {row['story_id']:<8} {icon}{row['priority']:<7} "
              f"{row['story_points']:<8} {str(row['title'])[:40]}")

# ============================================
print("\n\n[STEP 2] JSON OUTPUT FOR MEMBER 3...")
# ============================================

import json

# Build JSON structure for Member 3
output_json = {
    "sprint_plan": [],
    "metadata": {
        "total_stories": len(df),
        "total_sprints": df["sprint_number"].nunique(),
        "total_story_points": int(df["story_points"].sum()),
        "sprint_capacity": SPRINT_CAPACITY,
        "sprint_length_days": SPRINT_LENGTH,
        "team_size": NUM_DEVELOPERS,
    }
}

for sprint_num in sorted(df["sprint_number"].unique()):
    sprint_df = df[df["sprint_number"] == sprint_num]

    sprint_data = {
        "sprint_number": int(sprint_num),
        "total_story_points": int(sprint_df["story_points"].sum()),
        "capacity_used_percent": round(
            sprint_df["story_points"].sum() / SPRINT_CAPACITY * 100
        ),
        "stories": []
    }

    for _, row in sprint_df.iterrows():
        sprint_data["stories"].append({
            "story_id": row["story_id"],
            "title": row["title"],
            "priority": row["priority"],
            "story_points": int(row["story_points"]),
            "estimated_hours": int(row["story_points"] * 8),
        })

    output_json["sprint_plan"].append(sprint_data)

# Save JSON
json_path = os.path.join(base, "output_for_member3.json")
with open(json_path, "w") as f:
    json.dump(output_json, f, indent=2)

print("\nJSON output:")
print(json.dumps(output_json, indent=2))

print(f"\nJSON saved as: output_for_member3.json ✅")

# ============================================
print("\n[STEP 3] CSV OUTPUT FOR MEMBER 3...")
# ============================================

# Create a clean CSV with extra columns Member 3 needs
df_output = df.copy()
df_output["estimated_hours"]    = df_output["story_points"] * 8
df_output["sprint_length_days"] = SPRINT_LENGTH
df_output["team_size"]          = NUM_DEVELOPERS
df_output["capacity_per_sprint"]= SPRINT_CAPACITY

csv_path = os.path.join(base, "output_for_member3.csv")
df_output.to_csv(csv_path, index=False)

print("\nCSV output preview:")
print(df_output.to_string(index=False))
print(f"\nCSV saved as: output_for_member3.csv ✅")

print("\n" + "=" * 60)
print("OUTPUT FOR MEMBER 3 COMPLETE!")
print("=" * 60)
print("""
Member 3 receives two files:
  output_for_member3.json  ← structured data for their system
  output_for_member3.csv   ← spreadsheet format

From these files, Member 3 can:
  - See which stories are in each sprint
  - Know the priority of each story
  - Know the estimated effort in story points AND hours
  - Know the team size and sprint duration
  - Predict complexity and required man hours
""")