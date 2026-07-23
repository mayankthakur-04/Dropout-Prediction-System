"""
==========================================================================
 STEP 3: PERSONALIZED COUNSELING RECOMMENDATION ENGINE
==========================================================================
This is a RULE-BASED system (not a separate ML model) that sits on top
of the prediction model's output. It looks at WHICH features are driving
a specific student's risk score, and recommends targeted interventions.

WHY rule-based and not another ML model?
  - Counseling actions need to be explainable and auditable -- a teacher
    needs to know WHY a student was flagged and WHAT to do about it.
  - There's no large labeled dataset of "counseling action -> outcome" to
    train a model on (this would require years of real intervention data).
  - This is standard practice in real "decision support systems" -- ML for
    prediction, rules/expert-logic for actionable recommendations.

This directly implements:
  - Objective 4: Provide personalized counseling recommendations
  - Key Feature: Personalized counseling suggestions
  - Key Feature: Admin/teacher alert system
==========================================================================
"""

import pandas as pd
import joblib

OUT_DIR = "."

# Load the trained model and original dataset
model = joblib.load(f"{OUT_DIR}/dropout_model.pkl")
encoders = joblib.load(f"{OUT_DIR}/label_encoders.pkl")
feature_names = joblib.load(f"{OUT_DIR}/feature_names.pkl")
df = pd.read_csv(f"{OUT_DIR}/student_dropout_dataset.csv")

THRESHOLD = 0.42  # same as used in model training script

# --------------------------------------------------------------------
# Define recommendation rules.
# Each rule: (condition function, risk factor label, counseling action)
# These thresholds are illustrative -- in a real deployment, a college
# counselor/academic team should calibrate them based on institutional
# policy and past experience.
# --------------------------------------------------------------------
def generate_recommendations(student_row):
    """
    Takes a single student's data (as a pandas Series/dict) and returns
    a list of (issue, recommendation) tuples based on which risk factors
    are present for THIS student.
    """
    recs = []

    if student_row['attendance_pct'] < 60:
        recs.append((
            "Low attendance (%.1f%%)" % student_row['attendance_pct'],
            "Schedule a one-on-one meeting with class mentor to understand "
            "reasons for absence (health, financial, personal). Consider "
            "attendance recovery plan."
        ))

    if student_row['fee_due'] == 1 and student_row['fee_delay_days'] > 30:
        recs.append((
            "Fee due for %d+ days" % int(student_row['fee_delay_days']),
            "Refer to financial aid / scholarship cell. Check eligibility "
            "for fee installment plan or government scholarship schemes."
        ))

    if student_row['internal_marks_avg'] < 40 or student_row['backlogs'] >= 2:
        recs.append((
            "Weak academic performance (marks: %.1f, backlogs: %d)" %
            (student_row['internal_marks_avg'], student_row['backlogs']),
            "Enroll in peer tutoring / remedial classes. Assign faculty "
            "mentor for subject-specific support."
        ))

    if student_row['assignment_submission_rate'] < 50:
        recs.append((
            "Low assignment submission (%.0f%%)" % student_row['assignment_submission_rate'],
            "Check in on workload/time-management challenges. Consider "
            "flexible deadlines or study-skills workshop referral."
        ))

    if student_row['lms_login_freq_per_week'] < 2 and student_row['library_visits_per_month'] < 2:
        recs.append((
            "Very low academic engagement",
            "Encourage participation in study groups or peer-led sessions; "
            "investigate possible disengagement or personal distress."
        ))

    if student_row['first_generation_learner'] == 1 and student_row['distance_from_college_km'] > 30:
        recs.append((
            "First-generation learner commuting long distance (%.0f km)" %
            student_row['distance_from_college_km'],
            "Consider hostel accommodation support or local commute "
            "assistance; connect with first-gen student support group."
        ))

    if student_row['family_income_monthly'] < 15000 and student_row['scholarship_status'] == 0:
        recs.append((
            "Low family income, no current scholarship",
            "Proactively inform about applicable scholarships and "
            "fee-waiver schemes; refer to financial counselor."
        ))

    if not recs:
        recs.append((
            "No major single risk factor",
            "Risk likely from a combination of smaller factors. "
            "Recommend a general wellness/academic check-in."
        ))

    return recs


# --------------------------------------------------------------------
# Build per-student report for HIGH RISK students only (this is what
# would actually get sent to teachers/admin as "alerts")
# --------------------------------------------------------------------
df_model = df.drop(columns=['student_id'])
for col, le in encoders.items():
    df_model[col] = le.transform(df_model[col])

X = df_model[feature_names]
probabilities = model.predict_proba(X)[:, 1]

df['dropout_probability_pct'] = (probabilities * 100).round(1)
df['flagged_high_risk'] = probabilities >= THRESHOLD

high_risk_students = df[df['flagged_high_risk']].sort_values(
    'dropout_probability_pct', ascending=False
)

print(f"Total students flagged as HIGH RISK (alert-worthy): {len(high_risk_students)} "
      f"out of {len(df)} ({len(high_risk_students)/len(df)*100:.1f}%)\n")

# Generate a readable counseling report for the top 5 highest-risk students
# (in the real dashboard, this would run for ALL flagged students)
print("=" * 80)
print("SAMPLE COUNSELING ALERT REPORTS (Top 5 Highest-Risk Students)")
print("=" * 80)

report_rows = []
for _, row in high_risk_students.head(5).iterrows():
    print(f"\nStudent ID: {row['student_id']}")
    print(f"Dropout Risk Score: {row['dropout_probability_pct']}%")
    recs = generate_recommendations(row)
    for issue, action in recs:
        print(f"  ISSUE: {issue}")
        print(f"  -> ACTION: {action}\n")
        report_rows.append({
            'student_id': row['student_id'],
            'risk_score': row['dropout_probability_pct'],
            'issue': issue,
            'recommended_action': action
        })

# Save the FULL counseling report for all flagged students (not just top 5)
full_report_rows = []
for _, row in high_risk_students.iterrows():
    recs = generate_recommendations(row)
    for issue, action in recs:
        full_report_rows.append({
            'student_id': row['student_id'],
            'risk_score': row['dropout_probability_pct'],
            'issue': issue,
            'recommended_action': action
        })

report_df = pd.DataFrame(full_report_rows)
report_df.to_csv(f"{OUT_DIR}/counseling_recommendations.csv", index=False)
print(f"\nFull counseling recommendation report saved to: "
      f"{OUT_DIR}/counseling_recommendations.csv")
print(f"({len(report_df)} total recommendation entries across "
      f"{len(high_risk_students)} flagged students)")
