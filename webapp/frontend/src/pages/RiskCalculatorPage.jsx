import { useState } from "react";
import * as api from "../api/client";
import RiskBadge from "../components/RiskBadge";
import Card from "../components/Card";
import { PageHeader, ErrorBanner } from "./OverviewPage";

const DEFAULT_FORM = {
  attendance_pct: 75,
  internal_marks_avg: 60,
  prev_semester_pct: 62,
  cgpa: 6.2,
  backlogs: 1,
  assignment_submission_rate: 75,
  lms_login_freq_per_week: 5,
  library_visits_per_month: 4,
  extracurricular_participation: 0,
  family_income_monthly: 25000,
  first_generation_learner: 0,
  distance_from_college_km: 10,
  scholarship_status: 0,
  fee_due: 0,
  fee_delay_days: 0,
  gender: "Male",
  category: "General",
  hostel_or_dayscholar: "Day Scholar",
};

const NUMERIC_FIELDS = [
  ["attendance_pct", "Attendance (%)", 0, 100],
  ["internal_marks_avg", "Internal Marks (avg)", 0, 100],
  ["prev_semester_pct", "Previous Semester (%)", 0, 100],
  ["cgpa", "CGPA", 0, 10],
  ["backlogs", "Backlogs", 0, 10],
  ["assignment_submission_rate", "Assignment Submission (%)", 0, 100],
  ["lms_login_freq_per_week", "LMS Logins / week", 0, 30],
  ["library_visits_per_month", "Library Visits / month", 0, 25],
  ["family_income_monthly", "Family Income (₹/month)", 0, 300000],
  ["distance_from_college_km", "Distance from College (km)", 0, 100],
  ["fee_delay_days", "Fee Delay (days)", 0, 200],
];

export default function RiskCalculatorPage() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function updateField(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handlePredict() {
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form };
      // Ensure numeric fields are actually numbers, not strings from inputs
      NUMERIC_FIELDS.forEach(([key]) => {
        payload[key] = Number(payload[key]);
      });
      payload.backlogs = parseInt(payload.backlogs, 10);
      payload.lms_login_freq_per_week = parseInt(payload.lms_login_freq_per_week, 10);
      payload.library_visits_per_month = parseInt(payload.library_visits_per_month, 10);
      payload.fee_delay_days = parseInt(payload.fee_delay_days, 10);
      payload.extracurricular_participation = Number(payload.extracurricular_participation);
      payload.first_generation_learner = Number(payload.first_generation_learner);
      payload.scholarship_status = Number(payload.scholarship_status);
      payload.fee_due = Number(payload.fee_due);

      const res = await api.predictNewStudent(payload);
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Risk Calculator"
        subtitle="Enter a hypothetical student's details to see what the model would predict. Useful for exploring 'what-if' scenarios."
      />

      <div style={styles.grid}>
        <Card title="Student Details">
          <div style={styles.formGrid}>
            {NUMERIC_FIELDS.map(([key, label, min, max]) => (
              <label key={key} style={styles.label}>
                {label}
                <input
                  type="number"
                  min={min}
                  max={max}
                  value={form[key]}
                  onChange={(e) => updateField(key, e.target.value)}
                  style={styles.input}
                />
              </label>
            ))}

            <label style={styles.label}>
              Gender
              <select
                value={form.gender}
                onChange={(e) => updateField("gender", e.target.value)}
                style={styles.input}
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </label>

            <label style={styles.label}>
              Category
              <select
                value={form.category}
                onChange={(e) => updateField("category", e.target.value)}
                style={styles.input}
              >
                <option value="General">General</option>
                <option value="OBC">OBC</option>
                <option value="SC">SC</option>
                <option value="ST">ST</option>
                <option value="EWS">EWS</option>
              </select>
            </label>

            <label style={styles.label}>
              Accommodation
              <select
                value={form.hostel_or_dayscholar}
                onChange={(e) => updateField("hostel_or_dayscholar", e.target.value)}
                style={styles.input}
              >
                <option value="Day Scholar">Day Scholar</option>
                <option value="Hostel">Hostel</option>
              </select>
            </label>

            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={!!Number(form.fee_due)}
                onChange={(e) => updateField("fee_due", e.target.checked ? 1 : 0)}
              />
              Fee currently due
            </label>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={!!Number(form.scholarship_status)}
                onChange={(e) => updateField("scholarship_status", e.target.checked ? 1 : 0)}
              />
              Has scholarship
            </label>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={!!Number(form.first_generation_learner)}
                onChange={(e) => updateField("first_generation_learner", e.target.checked ? 1 : 0)}
              />
              First-generation learner
            </label>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={!!Number(form.extracurricular_participation)}
                onChange={(e) => updateField("extracurricular_participation", e.target.checked ? 1 : 0)}
              />
              Participates in extracurriculars
            </label>
          </div>

          <button onClick={handlePredict} disabled={loading} style={styles.button}>
            {loading ? "Calculating..." : "Predict Dropout Risk"}
          </button>
        </Card>

        <Card title="Prediction Result">
          {error && <ErrorBanner message={error} />}
          {!error && !result && (
            <p style={{ color: "var(--color-slate-500)", fontSize: 14 }}>
              Fill in the form and click "Predict Dropout Risk" to see the
              model's output for this hypothetical student.
            </p>
          )}
          {result && (
            <div style={styles.resultBlock}>
              <div style={styles.resultScore}>{result.dropout_probability}%</div>
              <RiskBadge tier={result.risk_tier} />
              <p style={styles.resultNote}>
                This is a live prediction from the trained Random Forest
                model, not a lookup from the existing dataset — demonstrating
                the model generalizes to new student profiles.
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}

const styles = {
  grid: {
    display: "grid",
    gridTemplateColumns: "1.4fr 1fr",
    gap: "var(--space-5)",
    alignItems: "start",
  },
  formGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "var(--space-4)",
    marginBottom: "var(--space-5)",
  },
  label: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
    fontSize: 12,
    fontWeight: 600,
    color: "var(--color-navy-800)",
  },
  checkboxLabel: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    fontSize: 13,
    fontWeight: 500,
    color: "var(--color-navy-800)",
  },
  input: {
    padding: "8px 10px",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--color-slate-300)",
    fontSize: 14,
  },
  button: {
    background: "var(--color-teal-600)",
    color: "white",
    border: "none",
    padding: "12px 20px",
    borderRadius: "var(--radius-sm)",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
  },
  resultBlock: {
    textAlign: "center",
    padding: "var(--space-5) 0",
  },
  resultScore: {
    fontFamily: "var(--font-display)",
    fontSize: 48,
    fontWeight: 700,
    marginBottom: "var(--space-3)",
  },
  resultNote: {
    fontSize: 12,
    color: "var(--color-slate-500)",
    marginTop: "var(--space-5)",
    lineHeight: 1.6,
  },
};
