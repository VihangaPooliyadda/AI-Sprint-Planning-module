import streamlit as st
import pandas as pd
import os
import pickle
import numpy as np
import json
from datetime import datetime

from database import (
    save_stories, load_stories,
    save_sprint_plan, load_sprint_plan,
    log_change, load_change_history,
    init_db
)
init_db()

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Sprint Planning System",
    page_icon="🤖",
    layout="wide"
)

# ============================================================
# BASE PATH
# ============================================================

base = os.path.join("C:", os.sep, "Users", "lap.lk", "Desktop", "Research 4.1")

# ============================================================
# LOAD MODELS
# ============================================================

@st.cache_resource
def load_models():
    with open(os.path.join(base, "priority_model.pkl"), "rb") as f:
        priority_model = pickle.load(f)
    with open(os.path.join(base, "priority_tfidf.pkl"), "rb") as f:
        tfidf = pickle.load(f)
    with open(os.path.join(base, "effort_model.pkl"), "rb") as f:
        effort_model = pickle.load(f)
    return priority_model, tfidf, effort_model

priority_model, tfidf, effort_model = load_models()

# ============================================================
# SESSION STATE
# ============================================================

if "user_stories" not in st.session_state:
    st.session_state.user_stories = []
if "sprint_plan" not in st.session_state:
    st.session_state.sprint_plan = {}
if "sprint_capacity" not in st.session_state:
    st.session_state.sprint_capacity = 30

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1F4E79, #2E75B6);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="main-header">
    <h1>🤖 AI Sprint Planning System</h1>
    <p>Research Component — Sprint Planning & Allocation | Member 2</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📌 Navigation")
st.sidebar.markdown("---")

page = st.sidebar.radio("Go to", [
    "🏠  Dashboard",
    "📝  Add User Stories",
    "🚀  Generate Sprint Plan",
    "⚠️  Re-planning",
    "📤  Output for Member 3",
    "📊  Model Performance",
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
high_count = sum(1 for s in st.session_state.user_stories if s.get("priority") == "HIGH")
low_count  = sum(1 for s in st.session_state.user_stories if s.get("priority") == "LOW")
st.sidebar.metric("Total Stories",    len(st.session_state.user_stories))
st.sidebar.metric("HIGH Priority",    high_count)
st.sidebar.metric("LOW Priority",     low_count)
st.sidebar.metric("Sprints Generated", len(st.session_state.sprint_plan))

# ============================================================
# PAGE 1 — DASHBOARD
# ============================================================

if page == "🏠  Dashboard":

    st.header("🏠 Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Total Stories",   len(st.session_state.user_stories))
    with col2:
        st.metric("🔴 HIGH Priority",   high_count)
    with col3:
        st.metric("🎯 Priority Accuracy", "67.58%")
    with col4:
        st.metric("📈 Effort R² Score",  "0.992")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔧 System Status")
        st.success("✅ Priority Prediction Model — Loaded & Ready")
        st.success("✅ Effort Estimation Model   — Loaded & Ready")
        st.success("✅ Sprint Allocator          — Ready")
        st.success("✅ Dynamic Re-planner        — Ready")
        if st.session_state.sprint_plan:
            st.info(f"📅 Sprint plan active — {len(st.session_state.sprint_plan)} sprints")
        else:
            st.info("ℹ️ No sprint plan yet — Add stories and generate one")

    with col2:
        st.subheader("🔄 Pipeline Flow")
        st.markdown("""
        | Step | Component | Owner |
        |------|-----------|-------|
        | 1️⃣ | Requirement Elicitation & User Stories | Member 1 |
        | 2️⃣ | **Priority + Effort + Sprint Allocation** | **You (Member 2)** |
        | 3️⃣ | Resource Allocation & Man Hours | Member 3 |
        | 4️⃣ | Change Management & Scope Creep | Member 4 |
        """)

    st.divider()

    if st.session_state.user_stories:
        st.subheader("📋 Current User Stories")
        df_stories = pd.DataFrame(st.session_state.user_stories)
        display_cols = [c for c in ["story_id", "title", "priority", "confidence", "story_points"] if c in df_stories.columns]
        st.dataframe(df_stories[display_cols], use_container_width=True)
    else:
        st.info("📭 No user stories added yet. Go to Add User Stories to get started.")

# ============================================================
# PAGE 2 — ADD USER STORIES
# ============================================================

elif page == "📝  Add User Stories":

    st.header("📝 Add User Stories")
    st.markdown("Enter user stories received from **Member 1**")

    tab1, tab2 = st.tabs(["➕ Add Single Story", "📥 Load Sample Stories"])

    with tab1:
        with st.form("story_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                title       = st.text_input("Story Title *", placeholder="e.g. Fix critical login security vulnerability")
                description = st.text_area("Story Description *", placeholder="e.g. Users can bypass login using SQL injection...", height=120)
            with col2:
                story_id     = st.text_input("Story ID", value=f"US{len(st.session_state.user_stories)+1:03d}")
                story_points = st.number_input("Story Points", min_value=1, max_value=100, value=5)

            submitted = st.form_submit_button("➕ Add Story & Predict Priority", use_container_width=True, type="primary")

            if submitted:
                if title.strip() and description.strip():
                    full_text  = title + " " + description
                    features   = tfidf.transform([full_text])
                    pred       = priority_model.predict(features)[0]
                    proba      = priority_model.predict_proba(features)[0]
                    priority   = "HIGH" if pred == 1 else "LOW"
                    confidence = round(max(proba) * 100, 1)
                    story = {
                        "story_id":    story_id,
                        "title":       title,
                        "description": description,
                        "story_points": story_points,
                        "priority":    priority,
                        "confidence":  confidence,
                    }
                    st.session_state.user_stories.append(story)
                    save_stories(st.session_state.user_stories) 
                    icon = "🔴" if priority == "HIGH" else "🟢"
                    st.success(f"✅ Story {story_id} added! Priority: {icon} {priority} ({confidence}% confidence)")
                    st.rerun()
                else:
                    st.error("❌ Please fill in both Title and Description")

    with tab2:
        st.markdown("Click below to load 10 pre-defined sample stories for demonstration.")
        if st.button("📥 Load 10 Sample User Stories", type="primary", use_container_width=True):
            samples = [
                {"story_id": "US001", "title": "Fix critical security vulnerability in login system",   "description": "Users can bypass authentication using SQL injection attack on login form",          "story_points": 8},
                {"story_id": "US002", "title": "Add export to PDF feature for reports",                 "description": "Users need to export their monthly reports as PDF files for sharing",              "story_points": 5},
                {"story_id": "US003", "title": "Update color scheme on dashboard page",                 "description": "Minor visual update to match new brand guidelines requested by design team",       "story_points": 2},
                {"story_id": "US004", "title": "Payment gateway crashes on checkout",                   "description": "Checkout process fails with 500 error for all users blocking all purchases",       "story_points": 13},
                {"story_id": "US005", "title": "Add search filter to user management",                  "description": "Allow admins to filter users by role status and registration date",                "story_points": 5},
                {"story_id": "US006", "title": "Fix broken email notifications",                        "description": "Email notifications not being sent to users after recent deployment update",       "story_points": 3},
                {"story_id": "US007", "title": "Add dark mode toggle to settings",                      "description": "Users requested dark mode option in profile settings for better readability",      "story_points": 3},
                {"story_id": "US008", "title": "Database connection timeout under heavy load",          "description": "Server times out when more than 100 users connected simultaneously causing errors", "story_points": 8},
                {"story_id": "US009", "title": "Update help documentation links",                       "description": "Several documentation links in help section return 404 errors need updating",      "story_points": 1},
                {"story_id": "US010", "title": "Add two factor authentication for admin users",         "description": "Admins need 2FA to improve account security and prevent unauthorized access",       "story_points": 8},
            ]
            for s in samples:
                full_text  = s["title"] + " " + s["description"]
                features   = tfidf.transform([full_text])
                pred       = priority_model.predict(features)[0]
                proba      = priority_model.predict_proba(features)[0]
                s["priority"]   = "HIGH" if pred == 1 else "LOW"
                s["confidence"] = round(max(proba) * 100, 1)
            st.session_state.user_stories = samples
            st.session_state.sprint_plan  = {}
            save_stories(st.session_state.user_stories)
            st.success("✅ 10 sample stories loaded with priority predictions!")
            st.rerun()

    st.divider()

    if st.session_state.user_stories:
        st.subheader(f"📋 Current Stories ({len(st.session_state.user_stories)} total)")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Stories", len(st.session_state.user_stories))
        with col2:
            st.metric("🔴 HIGH Priority", sum(1 for s in st.session_state.user_stories if s["priority"] == "HIGH"))
        with col3:
            st.metric("Total Story Points", sum(s["story_points"] for s in st.session_state.user_stories))

        for i, story in enumerate(st.session_state.user_stories):
            icon = "🔴" if story["priority"] == "HIGH" else "🟢"
            with st.expander(f"{story['story_id']} | {icon} {story['priority']} | {story['story_points']} pts | {story['title']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Description:** {story['description']}")
                with col2:
                    st.write(f"**Points:** {story['story_points']}")
                    st.write(f"**Priority:** {icon} {story['priority']}")
                    st.write(f"**Confidence:** {story['confidence']}%")
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.user_stories.pop(i)
                        st.session_state.sprint_plan = {}
                        st.rerun()

        st.divider()
        if st.button("🗑️ Clear All Stories", type="secondary"):
            st.session_state.user_stories = []
            st.session_state.sprint_plan  = {}
            st.rerun()

# ============================================================
# PAGE 3 — GENERATE SPRINT PLAN
# ============================================================

elif page == "🚀  Generate Sprint Plan":

    st.header("🚀 Generate Sprint Plan")

    if not st.session_state.user_stories:
        st.warning("⚠️ No user stories found. Please add stories from the Add User Stories page first.")
    else:
        st.subheader("⚙️ Sprint Configuration")
        col1, col2, col3 = st.columns(3)
        with col1:
            sprint_capacity = st.number_input("Sprint Capacity (story points)", min_value=10, max_value=200, value=30)
        with col2:
            sprint_length = st.number_input("Sprint Length (days)", min_value=7, max_value=30, value=14)
        with col3:
            num_devs = st.number_input("Number of Developers", min_value=1, max_value=50, value=5)

        st.session_state.sprint_capacity = sprint_capacity

        if st.button("🚀 Generate Sprint Plan Now", type="primary", use_container_width=True):
            stories_sorted = sorted(
                st.session_state.user_stories,
                key=lambda x: (0 if x["priority"] == "HIGH" else 1, x["story_points"])
            )
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

            st.session_state.sprint_plan = sprints
            save_sprint_plan(sprints)
            st.success(f"✅ Sprint plan generated! {len(st.session_state.user_stories)} stories across {len(sprints)} sprints.")

        if st.session_state.sprint_plan:
            st.divider()
            st.subheader("📅 Generated Sprint Plan")

            total_pts_all = sum(sum(s["story_points"] for s in stories) for stories in st.session_state.sprint_plan.values())
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sprints",       len(st.session_state.sprint_plan))
            with col2:
                st.metric("Total Stories",       len(st.session_state.user_stories))
            with col3:
                st.metric("Total Story Points",  total_pts_all)

            st.divider()

            for sprint_num, stories in st.session_state.sprint_plan.items():
                total_pts  = sum(s["story_points"] for s in stories)
                high_c     = sum(1 for s in stories if s["priority"] == "HIGH")
                low_c      = sum(1 for s in stories if s["priority"] == "LOW")
                cap_pct    = min(int(total_pts / sprint_capacity * 100), 100)

                with st.expander(
                    f"📅 Sprint {sprint_num}  —  {total_pts}/{sprint_capacity} pts ({cap_pct}%)  |  🔴 {high_c} HIGH   🟢 {low_c} LOW",
                    expanded=True
                ):
                    st.progress(cap_pct / 100)
                    st.markdown(f"**Duration:** {sprint_length} days  |  **Team:** {num_devs} developers")
                    st.markdown("---")

                    for story in stories:
                        icon = "🔴" if story["priority"] == "HIGH" else "🟢"
                        c1, c2, c3, c4 = st.columns([1, 5, 2, 1])
                        with c1:
                            st.write(f"**{story['story_id']}**")
                        with c2:
                            st.write(story["title"])
                        with c3:
                            st.write(f"{icon} {story['priority']} ({story.get('confidence','N/A')}%)")
                        with c4:
                            st.write(f"**{story['story_points']} pts**")

# ============================================================
# PAGE 4 — RE-PLANNING
# ============================================================

elif page == "⚠️  Re-planning":

    st.header("⚠️ Dynamic Re-planning")
    st.markdown("Handles scope change alerts from **Member 4 (Change Management)**")
    st.info("When Member 4 detects a scope change they notify your component. You process the change and re-generate the sprint plan.")

    with st.form("replan_form"):
        st.subheader("📨 Change Alert from Member 4")

        col1, col2 = st.columns(2)
        with col1:
            change_type      = st.selectbox("Change Type", ["NEW_STORY_ADDED", "STORY_REMOVED", "STORY_MODIFIED", "PRIORITY_CHANGED"])
            story_id_change  = st.text_input("Story ID", placeholder="e.g. US011")
            urgency          = st.selectbox("Urgency", ["CRITICAL", "HIGH", "MEDIUM", "LOW"])
        with col2:
            change_title       = st.text_input("Story Title",   placeholder="Title of new or modified story")
            change_description = st.text_area("Description",    placeholder="Describe the change...", height=100)
            change_points      = st.number_input("Story Points", min_value=1, max_value=100, value=8)

        change_reason = st.text_input("Reason for Change", placeholder="Why is this change happening?")
        apply_btn     = st.form_submit_button("⚡ Apply Change & Re-plan Sprints", use_container_width=True, type="primary")

    if apply_btn:
        if not st.session_state.user_stories:
            st.error("❌ No stories exist yet. Add stories and generate a sprint plan first.")
        elif not story_id_change:
            st.error("❌ Please enter a Story ID")
        else:
            if change_type == "NEW_STORY_ADDED":
                existing_ids = [s["story_id"] for s in st.session_state.user_stories]
                if story_id_change in existing_ids:
                    st.warning(f"⚠️ Story {story_id_change} already exists! Use a different Story ID.")
                else:
                    full_text  = change_title + " " + change_description
                    features   = tfidf.transform([full_text])
                    pred       = priority_model.predict(features)[0]
                    proba      = priority_model.predict_proba(features)[0]
                    priority   = "HIGH" if pred == 1 else "LOW"
                    confidence = round(max(proba) * 100, 1)
                    new_story  = {
                        "story_id":    story_id_change,
                        "title":       change_title,
                        "description": change_description,
                        "story_points": change_points,
                        "priority":    priority,
                        "confidence":  confidence,
                    }
                    st.session_state.user_stories.append(new_story)
                    st.session_state.sprint_plan = {}
                    log_change(change_type, story_id_change, reason=change_reason)
                    icon = "🔴" if priority == "HIGH" else "🟢"
                    log_change("NEW_STORY_ADDED", story_id_change, new_value=priority, reason=change_reason)
                    st.success(f"✅ Story {story_id_change} added! Priority: {icon} {priority} ({confidence}%)")
                    st.info("🔄 Sprint plan cleared. Go to Generate Sprint Plan to re-allocate.")

            elif change_type == "STORY_REMOVED":
                before = len(st.session_state.user_stories)
                st.session_state.user_stories = [
                    s for s in st.session_state.user_stories
                    if s["story_id"] != story_id_change
                ]
                st.session_state.sprint_plan = {}
                log_change(change_type, story_id_change, reason=change_reason)
                if len(st.session_state.user_stories) < before:
                    log_change("STORY_REMOVED", story_id_change, reason=change_reason)
                    st.success(f"✅ Story {story_id_change} removed successfully!")
                    st.info("🔄 Sprint plan cleared. Go to Generate Sprint Plan to re-allocate.")
                else:
                    st.warning(f"⚠️ Story {story_id_change} not found in current list.")

            elif change_type == "STORY_MODIFIED":
                found = False
                for s in st.session_state.user_stories:
                    if s["story_id"] == story_id_change:
                        s["story_points"] = change_points
                        if change_title:
                            s["title"] = change_title
                        found = True
                        break
                st.session_state.sprint_plan = {}
                log_change(change_type, story_id_change, reason=change_reason)
                if found:
                    log_change("STORY_MODIFIED", story_id_change, reason=change_reason)
                    st.success(f"✅ Story {story_id_change} updated successfully!")
                    st.info("🔄 Sprint plan cleared. Go to Generate Sprint Plan to re-allocate.")
                else:
                    st.warning(f"⚠️ Story {story_id_change} not found.")

            elif change_type == "PRIORITY_CHANGED":
                found = False
                for s in st.session_state.user_stories:
                    if s["story_id"] == story_id_change:
                        old_priority = s["priority"]
                        s["priority"] = "HIGH" if urgency in ["CRITICAL", "HIGH"] else "LOW"
                        found = True
                        log_change("PRIORITY_CHANGED", story_id_change, old_value=old_priority, new_value=s['priority'], reason=change_reason)
                        st.success(f"✅ Priority changed: {old_priority} → {s['priority']}")
                        st.info("🔄 Sprint plan cleared. Go to Generate Sprint Plan to re-allocate.")
                        break
                st.session_state.sprint_plan = {}
                log_change(change_type, story_id_change, reason=change_reason)
                if not found:
                    st.warning(f"⚠️ Story {story_id_change} not found.")

# ============================================================
# PAGE 5 — OUTPUT FOR MEMBER 3
# ============================================================

elif page == "📤  Output for Member 3":

    st.header("📤 Output for Member 3")
    st.markdown("Structured output for **Member 3 (Resource Allocation)**")

    if not st.session_state.sprint_plan:
        st.warning("⚠️ No sprint plan generated yet. Please go to Generate Sprint Plan first.")
    else:
        output_rows = []
        for sprint_num, stories in st.session_state.sprint_plan.items():
            for story in stories:
                output_rows.append({
                    "sprint_number":           sprint_num,
                    "story_id":                story["story_id"],
                    "title":                   story["title"],
                    "priority":                story["priority"],
                    "priority_confidence_pct": story.get("confidence", "N/A"),
                    "story_points":            story["story_points"],
                    "estimated_hours":         story["story_points"] * 8,
                    "sprint_length_days":      14,
                    "team_size":               5,
                })

        df_out = pd.DataFrame(output_rows)

        st.subheader("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Stories",        len(df_out))
        with col2:
            st.metric("Total Sprints",        df_out["sprint_number"].nunique())
        with col3:
            st.metric("Total Story Points",   int(df_out["story_points"].sum()))
        with col4:
            st.metric("Total Est. Hours",     int(df_out["estimated_hours"].sum()))

        st.divider()
        st.subheader("📋 Full Output Table")
        st.dataframe(df_out, use_container_width=True)

        st.divider()
        st.subheader("⬇️ Download Files for Member 3")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Download CSV",
                data=df_out.to_csv(index=False),
                file_name="output_for_member3.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
        with col2:
            st.download_button(
                label="⬇️ Download JSON",
                data=df_out.to_json(orient="records", indent=2),
                file_name="output_for_member3.json",
                mime="application/json",
                use_container_width=True
            )

        st.divider()
        st.subheader("📌 What Member 3 Does With This Data")
        st.markdown("""
        | Field | Used By Member 3 For |
        |-------|---------------------|
        | `priority` | Assign best developers to HIGH priority stories first |
        | `story_points` | Calculate workload per developer |
        | `estimated_hours` | Schedule developer time per sprint |
        | `sprint_number` | Know which sprint each resource is needed |
        | `team_size` | Plan total resource availability |
        """)

# ============================================================
# PAGE 6 — MODEL PERFORMANCE
# ============================================================

elif page == "📊  Model Performance":

    st.header("📊 Model Performance & Evaluation")

    tab1, tab2, tab3 = st.tabs([
        "🎯 Priority Prediction",
        "⏱️ Effort Estimation",
        "📋 Research Summary"
    ])

    with tab1:
        st.subheader("Priority Prediction — Random Forest Classifier")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy",         "67.58%")
        with col2:
            st.metric("F1 Score",         "0.673")
        with col3:
            st.metric("Training Samples", "66,175")
        with col4:
            st.metric("Test Samples",     "16,544")

        st.divider()
        st.subheader("Model Comparison")
        st.dataframe(pd.DataFrame({
            "Model":    ["Random Forest", "Logistic Regression", "Linear SVM", "Naive Bayes"],
            "Accuracy": ["67.58%", "66.77%", "66.51%", "65.35%"],
            "F1 Score": ["0.673",  "0.666",  "0.664",  "0.650"],
            "Rank":     ["🥇 Best", "🥈 2nd", "🥉 3rd", "4th"],
        }), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Confusion Matrix")
        st.dataframe(pd.DataFrame({
            "":               ["Actual LOW", "Actual HIGH"],
            "Predicted LOW":  [6697, 3114],
            "Predicted HIGH": [2250, 4483],
        }), use_container_width=True, hide_index=True)
        st.caption("Correctly classified: 6697 + 4483 = 11,180 out of 16,544 test samples")

    with tab2:
        st.subheader("Effort Estimation — Random Forest Regressor")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("R² Score",         "0.992")
        with col2:
            st.metric("MAE",              "1.78 pts")
        with col3:
            st.metric("CV R² Average",    "0.794")
        with col4:
            st.metric("Training Samples", "190")

        st.divider()
        st.subheader("Feature Importance")
        st.dataframe(pd.DataFrame({
            "Feature": [
                "completedIssuesInitialEstimateSum",
                "completedIssuesCount",
                "points_per_dev_per_day",
                "totalNumberOfIssues",
                "SprintLength",
                "NoOfDevelopers",
            ],
            "Importance":  [0.931, 0.051, 0.004, 0.003, 0.002, 0.002],
            "Percentage":  ["93.1%", "5.1%", "0.4%", "0.3%", "0.2%", "0.2%"],
        }), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Model Comparison")
        st.dataframe(pd.DataFrame({
            "Model":    ["Random Forest",   "Linear Regression"],
            "MAE":      ["1.78 pts",        "1.96 pts"],
            "R² Score": ["0.992",           "0.994"],
            "Rank":     ["🥇 Best",         "🥈 2nd"],
        }), use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Research Summary")
        st.markdown("""
        ### Datasets Used
        | Dataset | Size | Used For |
        |---------|------|----------|
        | GitHub Issues (cross-project_norm.csv) | 82,719 issues | Priority Prediction |
        | Aurora Sprints | 40 sprints | Effort Estimation |
        | MESO Sprints | 96 sprints | Effort Estimation |
        | Spring XD Sprints | 66 sprints | Effort Estimation |
        | Usergrid Sprints | 36 sprints | Effort Estimation |

        ### Key Findings
        | Finding | Value |
        |---------|-------|
        | Best model for priority prediction | Random Forest (67.58%) |
        | Best model for effort estimation | Random Forest (R²=0.992) |
        | Most important effort feature | Initial estimate sum (93.1%) |
        | Sprint allocation method | Greedy Bin Packing |
        | Dynamic re-planning | Triggered by Member 4 change alerts |

        ### Research Gap Addressed
        > *Existing studies addressed priority prediction, effort estimation, and sprint
        allocation as separate tasks. This research proposes an integrated pipeline
        combining all three tasks with dynamic re-planning capability, which has not
        been done in prior work.*
        """)