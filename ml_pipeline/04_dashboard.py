"""
==========================================================================
 STEP 4: STREAMLIT DASHBOARD - RISK PREDICTION & COUNSELING SYSTEM
==========================================================================
This dashboard ties together everything from scripts 1-3 into one
interactive view, covering the remaining spec items:

  - Key Feature: Risk Prediction Dashboard
  - Key Feature: Dropout probability score (already have this, now visualized)
  - Key Feature: Admin/teacher alert system
  - Key Feature: Progress monitoring after counseling (SIMULATED - see note
    below; we don't have real longitudinal data, so this section clearly
    labels itself as a demo/illustrative feature)
  - Objective 3: Generate early warning alerts for institutions

HOW TO RUN THIS:
    1. Make sure scripts 1, 2, and 3 have already been run (this dashboard
       just READS their output files, it doesn't regenerate anything).
    2. In your terminal, in this same folder, run:
           streamlit run 04_dashboard.py
    3. It will open automatically in your browser (usually localhost:8501).
==========================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import os

# --------------------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit command)
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Dropout Prediction & Counseling System",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------------------------
# LOAD DATA (cached so it doesn't reload on every click)
# --------------------------------------------------------------------
@st.cache_data
def load_data():
    # Base student dataset (has all the raw features)
    students = pd.read_csv("student_dropout_dataset.csv")

    # Risk scores from the trained model
    risk = pd.read_csv("student_risk_scores.csv")[['student_id', 'dropout_probability', 'risk_tier']]

    # Merge so we have features + risk score + tier in ONE table
    merged = students.merge(risk, on='student_id', how='left')

    # Counseling recommendations (one row per issue, multiple rows per student)
    recs = pd.read_csv("counseling_recommendations.csv")

    # Model metrics (for the "Model Performance" tab)
    metrics = {}
    if os.path.exists("model_metrics.json"):
        with open("model_metrics.json") as f:
            metrics = json.load(f)

    return merged, recs, metrics


# Friendly error if scripts haven't been run yet
required_files = ["student_dropout_dataset.csv", "student_risk_scores.csv", "counseling_recommendations.csv"]
missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    st.error(
        f"Missing file(s): {', '.join(missing)}.\n\n"
        f"Please run 01_generate_dataset.py, 02_train_model.py, and "
        f"03_counseling_engine.py (in that order) in this same folder "
        f"before launching the dashboard."
    )
    st.stop()

df, recs_df, metrics = load_data()

# --------------------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------------------
st.sidebar.title("🎓 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "📊 Overview",
        "⚠️ Risk Prediction Dashboard",
        "🔔 Teacher/Admin Alerts",
        "🧑‍🎓 Student Drill-Down",
        "📈 Progress Monitoring (Demo)",
        "🧠 Model Performance",
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "AI-Based Dropout Prediction and Counseling System\n\n"
    "Built on synthetic data modeled after Indian college records "
    "(attendance, marks, fees, family income, etc.)."
)

# ==========================================================================
# PAGE 1: OVERVIEW
# ==========================================================================
if page == "📊 Overview":
    st.title("📊 Institution Overview")
    st.caption("A snapshot of student risk across the institution.")

    total_students = len(df)
    high_risk = (df['risk_tier'] == 'High Risk').sum()
    medium_risk = (df['risk_tier'] == 'Medium Risk').sum()
    low_risk = (df['risk_tier'] == 'Low Risk').sum()
    avg_risk = df['dropout_probability'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", f"{total_students:,}")
    col2.metric("High Risk", f"{high_risk:,}", f"{high_risk/total_students*100:.1f}%")
    col3.metric("Medium Risk", f"{medium_risk:,}", f"{medium_risk/total_students*100:.1f}%")
    col4.metric("Avg. Dropout Risk", f"{avg_risk:.1f}%")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Risk Tier Distribution")
        tier_counts = df['risk_tier'].value_counts().reindex(
            ['High Risk', 'Medium Risk', 'Low Risk']
        )
        fig = px.pie(
            values=tier_counts.values,
            names=tier_counts.index,
            color=tier_counts.index,
            color_discrete_map={
                'High Risk': '#d62728',
                'Medium Risk': '#ff7f0e',
                'Low Risk': '#2ca02c'
            },
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Dropout Probability Distribution")
        fig2 = px.histogram(
            df, x='dropout_probability', nbins=30,
            labels={'dropout_probability': 'Dropout Probability (%)'},
            color_discrete_sequence=['#4C72B0']
        )
        fig2.update_layout(yaxis_title="Number of Students")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Risk by Key Factors")
    factor = st.selectbox(
        "Compare risk tier against:",
        ['attendance_pct', 'internal_marks_avg', 'family_income_monthly',
         'distance_from_college_km', 'fee_delay_days', 'assignment_submission_rate']
    )
    fig3 = px.box(
        df, x='risk_tier', y=factor, color='risk_tier',
        category_orders={'risk_tier': ['Low Risk', 'Medium Risk', 'High Risk']},
        color_discrete_map={
            'High Risk': '#d62728', 'Medium Risk': '#ff7f0e', 'Low Risk': '#2ca02c'
        }
    )
    st.plotly_chart(fig3, use_container_width=True)


# ==========================================================================
# PAGE 2: RISK PREDICTION DASHBOARD
# ==========================================================================
elif page == "⚠️ Risk Prediction Dashboard":
    st.title("⚠️ Risk Prediction Dashboard")
    st.caption("Filter and search all students by dropout risk.")

    col1, col2, col3 = st.columns(3)
    with col1:
        tier_filter = st.multiselect(
            "Risk Tier", ['High Risk', 'Medium Risk', 'Low Risk'],
            default=['High Risk', 'Medium Risk', 'Low Risk']
        )
    with col2:
        search_id = st.text_input("Search Student ID (e.g. STU1098)")
    with col3:
        sort_order = st.selectbox("Sort by risk", ["Highest first", "Lowest first"])

    filtered = df[df['risk_tier'].isin(tier_filter)]
    if search_id:
        filtered = filtered[filtered['student_id'].str.contains(search_id.strip(), case=False)]
    filtered = filtered.sort_values(
        'dropout_probability', ascending=(sort_order == "Lowest first")
    )

    st.write(f"Showing **{len(filtered)}** of {len(df)} students")

    display_cols = [
        'student_id', 'dropout_probability', 'risk_tier', 'attendance_pct',
        'internal_marks_avg', 'backlogs', 'fee_due', 'family_income_monthly'
    ]
    st.dataframe(
        filtered[display_cols].rename(columns={
            'dropout_probability': 'Dropout Risk (%)',
            'risk_tier': 'Risk Tier',
            'attendance_pct': 'Attendance (%)',
            'internal_marks_avg': 'Internal Marks',
            'backlogs': 'Backlogs',
            'fee_due': 'Fee Due',
            'family_income_monthly': 'Family Income (₹/mo)'
        }),
        use_container_width=True,
        hide_index=True,
        height=450
    )

    csv_export = filtered[display_cols].to_csv(index=False)
    st.download_button(
        "⬇️ Download filtered list as CSV", csv_export,
        file_name="filtered_risk_students.csv", mime="text/csv"
    )


# ==========================================================================
# PAGE 3: TEACHER/ADMIN ALERTS
# ==========================================================================
elif page == "🔔 Teacher/Admin Alerts":
    st.title("🔔 Early Warning Alerts")
    st.caption(
        "Students flagged as High Risk, requiring counselor/teacher attention. "
        "This view implements Objective 3 (early warning alerts)."
    )

    high_risk_df = df[df['risk_tier'] == 'High Risk'].sort_values(
        'dropout_probability', ascending=False
    )

    st.error(f"🚨 {len(high_risk_df)} students currently flagged as High Risk")

    for _, row in high_risk_df.head(25).iterrows():
        with st.expander(
            f"🔴 {row['student_id']}  —  Risk Score: {row['dropout_probability']}%"
        ):
            c1, c2, c3 = st.columns(3)
            c1.metric("Attendance", f"{row['attendance_pct']}%")
            c2.metric("Internal Marks", f"{row['internal_marks_avg']}")
            c3.metric("Backlogs", int(row['backlogs']))

            student_recs = recs_df[recs_df['student_id'] == row['student_id']]
            if not student_recs.empty:
                st.markdown("**Recommended Counseling Actions:**")
                for _, r in student_recs.iterrows():
                    st.markdown(f"- **Issue:** {r['issue']}")
                    st.markdown(f"  → *Action:* {r['recommended_action']}")
            else:
                st.markdown("_No specific issue flagged by rule engine._")

    if len(high_risk_df) > 25:
        st.info(f"Showing top 25 of {len(high_risk_df)} high-risk students. "
                f"Use the Risk Prediction Dashboard page to see all of them.")


# ==========================================================================
# PAGE 4: STUDENT DRILL-DOWN
# ==========================================================================
elif page == "🧑‍🎓 Student Drill-Down":
    st.title("🧑‍🎓 Individual Student Report")
    st.caption("Look up any student to see their full risk profile and counseling plan.")

    selected_id = st.selectbox("Select Student ID", sorted(df['student_id'].unique()))
    student = df[df['student_id'] == selected_id].iloc[0]

    col1, col2 = st.columns([1, 2])
    with col1:
        risk_color = {
            'High Risk': 'red', 'Medium Risk': 'orange', 'Low Risk': 'green'
        }[student['risk_tier']]
        st.markdown(f"### Risk Tier: :{risk_color}[{student['risk_tier']}]")
        st.metric("Dropout Probability", f"{student['dropout_probability']}%")

        # Simple gauge-style chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=student['dropout_probability'],
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#333333"},
                'steps': [
                    {'range': [0, 30], 'color': "#2ca02c"},
                    {'range': [30, 55], 'color': "#ff7f0e"},
                    {'range': [55, 100], 'color': "#d62728"},
                ]
            }
        ))
        fig.update_layout(height=250, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Student Profile")
        profile_cols = [
            'attendance_pct', 'internal_marks_avg', 'prev_semester_pct', 'cgpa',
            'backlogs', 'assignment_submission_rate', 'lms_login_freq_per_week',
            'library_visits_per_month', 'family_income_monthly',
            'first_generation_learner', 'distance_from_college_km',
            'scholarship_status', 'fee_due', 'fee_delay_days', 'gender',
            'category', 'hostel_or_dayscholar'
        ]
        profile_df = pd.DataFrame({
            'Attribute': profile_cols,
            'Value': [student[c] for c in profile_cols]
        })
        st.dataframe(profile_df, hide_index=True, use_container_width=True, height=300)

    st.markdown("---")
    st.markdown("### 🩺 Personalized Counseling Plan")
    student_recs = recs_df[recs_df['student_id'] == selected_id]
    if not student_recs.empty:
        for _, r in student_recs.iterrows():
            st.warning(f"**{r['issue']}**\n\n→ {r['recommended_action']}")
    else:
        st.success("No specific risk factors flagged for this student.")


# ==========================================================================
# PAGE 5: PROGRESS MONITORING (DEMO / SIMULATED)
# ==========================================================================
elif page == "📈 Progress Monitoring (Demo)":
    st.title("📈 Progress Monitoring After Counseling")
    st.warning(
        "⚠️ **Note for report/viva:** Our dataset is a single snapshot in "
        "time (no real before/after counseling records exist for synthetic "
        "data). This page SIMULATES what progress monitoring would look "
        "like once a college starts tracking real outcomes over multiple "
        "semesters. Be transparent about this in your report as a "
        "'future work / planned feature' rather than a fully validated one."
    )

    selected_id = st.selectbox(
        "Select a High-Risk student to simulate progress for",
        sorted(df[df['risk_tier'] == 'High Risk']['student_id'].unique())
    )
    student = df[df['student_id'] == selected_id].iloc[0]
    initial_risk = student['dropout_probability']

    st.markdown(f"**Initial Risk Score (before counseling):** {initial_risk}%")

    # Simulate a plausible improvement curve over 4 months post-counseling.
    # This uses a simple decay formula -- NOT a trained model -- purely to
    # illustrate what a real tracking chart would look like.
    months = ["Month 0\n(At Flagging)", "Month 1", "Month 2", "Month 3", "Month 4"]
    np.random.seed(hash(selected_id) % 1000)  # deterministic per student
    improvement_rate = np.random.uniform(0.08, 0.18)
    simulated_scores = [initial_risk]
    for _ in range(4):
        next_score = simulated_scores[-1] * (1 - improvement_rate)
        simulated_scores.append(round(next_score, 1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=simulated_scores, mode='lines+markers',
        line=dict(color='#4C72B0', width=3), marker=dict(size=10),
        name="Dropout Risk (%)"
    ))
    fig.add_hline(y=30, line_dash="dash", line_color="green",
                  annotation_text="Low Risk threshold")
    fig.update_layout(
        yaxis_title="Dropout Risk (%)", xaxis_title="Time since counseling",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"Simulated outcome: risk reduced from **{simulated_scores[0]}%** to "
        f"**{simulated_scores[-1]}%** over 4 months following counseling "
        f"intervention. In a real deployment, this would be computed by "
        f"re-running the trained model on the student's UPDATED attendance/"
        f"marks/engagement data each month, not simulated."
    )


# ==========================================================================
# PAGE 6: MODEL PERFORMANCE
# ==========================================================================
elif page == "🧠 Model Performance":
    st.title("🧠 Model Performance & Explainability")
    st.caption("Evaluation metrics and feature importance from the trained model.")

    if metrics:
        rf = metrics.get('random_forest_tuned_threshold', {})
        lr = metrics.get('logistic_regression', {})

        st.subheader("Random Forest (Main Model) — Tuned Threshold")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Accuracy", f"{rf.get('accuracy', 0):.2f}")
        c2.metric("Precision", f"{rf.get('precision', 0):.2f}")
        c3.metric("Recall", f"{rf.get('recall', 0):.2f}")
        c4.metric("F1-Score", f"{rf.get('f1', 0):.2f}")
        c5.metric("ROC-AUC", f"{rf.get('auc', 0):.2f}")

        st.subheader("Logistic Regression (Baseline)")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Accuracy", f"{lr.get('accuracy', 0):.2f}")
        c2.metric("Precision", f"{lr.get('precision', 0):.2f}")
        c3.metric("Recall", f"{lr.get('recall', 0):.2f}")
        c4.metric("F1-Score", f"{lr.get('f1', 0):.2f}")
        c5.metric("ROC-AUC", f"{lr.get('auc', 0):.2f}")

        st.caption(
            f"Dataset: {metrics.get('dataset_size', 'N/A')} students | "
            f"Dropout rate: {metrics.get('dropout_rate_pct', 'N/A')}% | "
            f"Classification threshold tuned to "
            f"{metrics.get('tuned_threshold_value', 0.5)} to prioritize recall."
        )
    else:
        st.warning("model_metrics.json not found — run 02_train_model.py first.")

    st.markdown("---")
    st.subheader("Top Factors Contributing to Dropout")
    if os.path.exists("feature_importance.csv"):
        fi = pd.read_csv("feature_importance.csv").sort_values('importance', ascending=True)
        fig = px.bar(
            fi.tail(10), x='importance', y='feature', orientation='h',
            color_discrete_sequence=['#4C72B0']
        )
        fig.update_layout(yaxis_title="", xaxis_title="Importance Score", height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("feature_importance.csv not found — run 02_train_model.py first.")
