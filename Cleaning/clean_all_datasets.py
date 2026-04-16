import pandas as pd
import os

# All files are inside Datasets RAW folder
raw = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1", "Datasets RAW")

# Cleaned files will be saved to Research 4.1 folder
save = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1")

print("=" * 60)
print("CLEANING ALL DATASETS")
print("=" * 60)

# ============================================
print("\n[1/5] CLEANING PRIORITY DATASET...")
# ============================================

df_priority = pd.read_csv(os.path.join(raw, "cross-project_norm.csv"))
print(f"    Loaded: {df_priority.shape}")

# Select useful columns
priority_cols = [
    "title_processed", "body_processed", "ft_issue_type",
    "num_labels", "title_processed_words_num", "body_processed_words_num",
    "num_of_urls", "has_code", "has_commit", "has_assignee",
    "is_pull_request", "num_comments", "num_events", "has_milestone",
    "time_to_discuss", "author_followers", "author_public_repos",
    "author_issue_counts", "author_account_age", "author_repo_cntrb",
    "body_sentistrenght_p", "positive_body_polarity", "body_subjectivity",
    "repo_label_biclass", "actual_label_cat",
]
df_priority = df_priority[priority_cols].copy()

# Remove missing values
df_priority = df_priority.dropna()

# Clean text
df_priority["title_processed"] = df_priority["title_processed"].fillna("").str.strip().str.lower()
df_priority["body_processed"] = df_priority["body_processed"].fillna("").str.strip().str.lower()

# Remove rows where both title and body are empty
df_priority = df_priority[
    (df_priority["title_processed"] != "") |
    (df_priority["body_processed"] != "")
]

# Combine title and body into one text column
df_priority["full_text"] = df_priority["title_processed"] + " " + df_priority["body_processed"]

# Encode priority (1 = HIGH, 0 = LOW)
df_priority["priority_label"] = df_priority["repo_label_biclass"].map({
    "HIGH": 1, "LOW": 0
})

# Make issue type readable
df_priority["issue_type"] = df_priority["ft_issue_type"].map({
    1.0: "Bug", 0.5: "Enhancement", 0.0: "Support"
})

# Save
df_priority.to_csv(os.path.join(save, "clean_priority.csv"), index=False)
print(f"    Clean shape: {df_priority.shape}")
print(f"    Priority distribution:")
print(f"      HIGH: {(df_priority['priority_label']==1).sum()}")
print(f"      LOW:  {(df_priority['priority_label']==0).sum()}")
print("    Saved as: clean_priority.csv ✅")

# ============================================
print("\n[2/5] LOADING AURORA SPRINTS...")
# ============================================

df1 = pd.read_csv(os.path.join(raw, "Aurora Sprints 41.csv"))
df1 = df1.rename(columns={"total": "totalNumberOfIssues"})
df1["project"] = "Aurora"
print(f"    Loaded: {df1.shape}")

# ============================================
print("\n[3/5] LOADING MESO SPRINTS...")
# ============================================

df2 = pd.read_csv(os.path.join(raw, "MESO Sprint 96.csv"))
df2["project"] = "MESO"
print(f"    Loaded: {df2.shape}")

# ============================================
print("\n[4/5] LOADING SPRING XD SPRINTS...")
# ============================================

df3 = pd.read_csv(os.path.join(raw, "Spring XD Sprints 67.csv"))
df3["project"] = "SpringXD"
print(f"    Loaded: {df3.shape}")

# ============================================
print("\n[5/5] LOADING USERGRID SPRINTS...")
# ============================================

df4 = pd.read_csv(os.path.join(raw, "Usergrid Sprints 36.csv"))
df4 = df4.rename(columns={
    "total": "totalNumberOfIssues",
    "issuesCompletedInAnotherSprintEstimateSum1": "issuesCompletedInAnotherSprintEstimateSum"
})
df4["project"] = "Usergrid"
print(f"    Loaded: {df4.shape}")

# ============================================
print("\n--- COMBINING ALL SPRINT DATASETS ---")
# ============================================

df_sprints = pd.concat([df1, df2, df3, df4], ignore_index=True)
print(f"Combined shape: {df_sprints.shape}")

# Remove missing rows
df_sprints = df_sprints.dropna()
print(f"After removing missing: {df_sprints.shape}")

# Select useful columns
sprint_cols = [
    "project", "sprintId", "sprintName", "sprintState",
    "sprintStartDate", "sprintEndDate", "SprintLength", "NoOfDevelopers",
    "totalNumberOfIssues", "completedIssuesCount",
    "completedIssuesInitialEstimateSum", "completedIssuesEstimateSum",
    "issuesNotCompletedInCurrentSprint", "issuesNotCompletedEstimateSum",
    "puntedIssues", "puntedIssuesEstimateSum",
    "issueKeysAddedDuringSprint",
    "issuesCompletedInAnotherSprint",
    "issuesCompletedInAnotherSprintEstimateSum",
]
df_sprints = df_sprints[sprint_cols].copy()

# Create new useful columns
df_sprints["sprint_velocity"] = df_sprints["completedIssuesEstimateSum"]

df_sprints["completion_rate"] = (
    df_sprints["completedIssuesCount"] /
    df_sprints["totalNumberOfIssues"].replace(0, 1)
).round(2)

df_sprints["scope_creep"] = df_sprints["issueKeysAddedDuringSprint"].apply(
    lambda x: 1 if str(x) not in ["0", "[]", "", "nan"] else 0
)

df_sprints["estimation_accuracy"] = (
    df_sprints["completedIssuesEstimateSum"] /
    df_sprints["completedIssuesInitialEstimateSum"].replace(0, 1)
).round(2)

df_sprints["points_per_dev_per_day"] = (
    df_sprints["completedIssuesEstimateSum"] /
    (df_sprints["NoOfDevelopers"] * df_sprints["SprintLength"]).replace(0, 1)
).round(2)

# Remove invalid rows
df_sprints = df_sprints[df_sprints["SprintLength"] > 0]
df_sprints = df_sprints[df_sprints["NoOfDevelopers"] > 0]
df_sprints = df_sprints[df_sprints["totalNumberOfIssues"] > 0]

# Save
df_sprints.to_csv(os.path.join(save, "clean_sprints.csv"), index=False)
print(f"Final sprint shape: {df_sprints.shape}")
print(f"Project distribution:")
print(df_sprints["project"].value_counts().to_string())
print(f"Sprint velocity stats:")
print(df_sprints["sprint_velocity"].describe().round(2).to_string())
print("Saved as: clean_sprints.csv ✅")

# ============================================
print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(f"""
clean_priority.csv
  Rows    : {df_priority.shape[0]}
  Columns : {df_priority.shape[1]}
  Use for : Priority Prediction Model
  Target  : priority_label (1=HIGH, 0=LOW)

clean_sprints.csv
  Rows    : {df_sprints.shape[0]}
  Columns : {df_sprints.shape[1]}
  Use for : Effort Estimation + Sprint Allocation
  Target  : sprint_velocity
""")
print("ALL DATASETS CLEANED SUCCESSFULLY! ✅")