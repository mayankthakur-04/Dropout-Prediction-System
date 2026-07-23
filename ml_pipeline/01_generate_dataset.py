"""
==========================================================================
 STEP 1: GENERATE SYNTHETIC DATASET FOR INDIAN COLLEGE DROPOUT PREDICTION
==========================================================================
WHY SYNTHETIC DATA?
Real student dropout data from Indian colleges is private and not publicly
released. For academic projects, it is standard practice to generate a
REALISTIC synthetic dataset that mirrors real-world patterns (this should
be clearly stated in your project report under "Data Source / Limitations").

We simulate data the way it would actually exist across different college
departments:
  - Exam Cell        -> marks, backlogs, CGPA
  - Attendance Office -> attendance %
  - Accounts Office   -> fee due status
  - Admission Office  -> family income, category, hostel/day-scholar
  - LMS/Library       -> engagement metrics

The DROPOUT LABEL is generated using a "risk score" logic (not random!) so
that the dataset has genuine, learnable patterns -- e.g., a student with
low attendance + fee due + low marks is MUCH more likely to be marked as
a dropout than a student who is doing fine. This makes the ML model's job
meaningful instead of just memorizing noise.
==========================================================================
"""

import numpy as np
import pandas as pd

# Setting a seed means every time you run this script, you get the SAME
# "random" data. Useful for reproducibility (a marks-winning detail to
# mention in your viva).
np.random.seed(42)

N = 2000  # number of student records to simulate

# --------------------------------------------------------------------
# 1. ACADEMIC FEATURES
# --------------------------------------------------------------------
attendance_pct = np.random.normal(loc=78, scale=15, size=N).clip(30, 100)
internal_marks_avg = np.random.normal(loc=60, scale=18, size=N).clip(0, 100)
prev_semester_pct = np.random.normal(loc=62, scale=16, size=N).clip(0, 100)
backlogs = np.random.poisson(lam=1.2, size=N).clip(0, 8)
cgpa = (prev_semester_pct / 10).clip(0, 10).round(2)

# --------------------------------------------------------------------
# 2. ENGAGEMENT / BEHAVIORAL FEATURES
# --------------------------------------------------------------------
assignment_submission_rate = np.random.normal(loc=75, scale=20, size=N).clip(0, 100)
lms_login_freq_per_week = np.random.poisson(lam=5, size=N).clip(0, 30)
library_visits_per_month = np.random.poisson(lam=4, size=N).clip(0, 25)
extracurricular_participation = np.random.choice([0, 1], size=N, p=[0.65, 0.35])

# --------------------------------------------------------------------
# 3. SOCIO-ECONOMIC FEATURES
# --------------------------------------------------------------------
family_income_monthly = np.random.lognormal(mean=9.8, sigma=0.6, size=N).clip(5000, 200000).round(0)
first_generation_learner = np.random.choice([0, 1], size=N, p=[0.55, 0.45])
distance_from_college_km = np.random.exponential(scale=12, size=N).clip(0, 100).round(1)
scholarship_status = np.random.choice([0, 1], size=N, p=[0.7, 0.3])

# --------------------------------------------------------------------
# 4. FINANCIAL FEATURES
# --------------------------------------------------------------------
fee_due = np.random.choice([0, 1], size=N, p=[0.75, 0.25])
fee_delay_days = np.where(fee_due == 1,
                           np.random.poisson(lam=45, size=N).clip(1, 200),
                           0)

# --------------------------------------------------------------------
# 5. DEMOGRAPHIC FEATURES
# --------------------------------------------------------------------
gender = np.random.choice(['Male', 'Female'], size=N, p=[0.58, 0.42])
category = np.random.choice(['General', 'OBC', 'SC', 'ST', 'EWS'], size=N,
                             p=[0.40, 0.30, 0.15, 0.07, 0.08])
hostel_or_dayscholar = np.random.choice(['Hostel', 'Day Scholar'], size=N, p=[0.4, 0.6])

# --------------------------------------------------------------------
# 6. BUILD THE DATAFRAME
# --------------------------------------------------------------------
df = pd.DataFrame({
    'student_id': [f"STU{1000+i}" for i in range(N)],
    'attendance_pct': attendance_pct.round(1),
    'internal_marks_avg': internal_marks_avg.round(1),
    'prev_semester_pct': prev_semester_pct.round(1),
    'cgpa': cgpa,
    'backlogs': backlogs,
    'assignment_submission_rate': assignment_submission_rate.round(1),
    'lms_login_freq_per_week': lms_login_freq_per_week,
    'library_visits_per_month': library_visits_per_month,
    'extracurricular_participation': extracurricular_participation,
    'family_income_monthly': family_income_monthly,
    'first_generation_learner': first_generation_learner,
    'distance_from_college_km': distance_from_college_km,
    'scholarship_status': scholarship_status,
    'fee_due': fee_due,
    'fee_delay_days': fee_delay_days,
    'gender': gender,
    'category': category,
    'hostel_or_dayscholar': hostel_or_dayscholar,
})

# --------------------------------------------------------------------
# 7. GENERATE THE DROPOUT LABEL USING A REALISTIC "RISK SCORE"
# --------------------------------------------------------------------
# This is the most important part. We build a weighted risk score from
# real-world risk factors. Higher score = higher dropout probability.
# We then add randomness (because real life isn't 100% deterministic)
# and threshold it into a binary label.

risk_score = (
    (100 - df['attendance_pct']) * 0.045 +
    (100 - df['internal_marks_avg']) * 0.025 +
    (100 - df['prev_semester_pct']) * 0.020 +
    df['backlogs'] * 0.55 +
    (100 - df['assignment_submission_rate']) * 0.015 +
    (10 - df['lms_login_freq_per_week'].clip(0, 10)) * 0.10 +
    df['fee_due'] * 1.4 +
    (df['fee_delay_days'] / 30) * 0.30 +
    df['first_generation_learner'] * 0.45 +
    (df['distance_from_college_km'] / 20) * 0.20 +
    (1 - df['scholarship_status']) * 0.15 +
    np.where(df['family_income_monthly'] < 15000, 0.8, 0)
)

# Add random noise so the relationship isn't perfectly clean (more realistic,
# and prevents the model from getting a "too good to be true" 100% accuracy)
risk_score += np.random.normal(0, 1.5, size=N)

# Convert risk score into a probability using a logistic (sigmoid) function,
# then sample the actual outcome -- this mimics real-world uncertainty.
# We shift the curve (subtract an extra constant) so that the overall
# dropout rate matches realistic Indian college figures (~12-15%), instead
# of an unrealistic 50%. The '-1.1' shift controls the base rate -- a more
# negative shift = lower overall dropout rate.
risk_score_scaled = (risk_score - risk_score.mean()) / risk_score.std()
dropout_probability = 1 / (1 + np.exp(-(risk_score_scaled - 1.75)))
dropout_label = (np.random.rand(N) < dropout_probability).astype(int)

df['dropout'] = dropout_label  # 1 = Dropout, 0 = Continuing/Graduated

# --------------------------------------------------------------------
# 8. SAVE TO CSV
# --------------------------------------------------------------------
output_path = "student_dropout_dataset.csv"
df.to_csv(output_path, index=False)

print(f"Dataset created with {N} records and {df.shape[1]} columns.")
print(f"Saved to: {output_path}")
print(f"\nDropout distribution:\n{df['dropout'].value_counts()}")
print(f"Dropout rate: {df['dropout'].mean()*100:.1f}%")
print(f"\nFirst 5 rows:\n{df.head()}")
