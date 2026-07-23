import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../api/client";
import RiskBadge from "../components/RiskBadge";
import { PageHeader, LoadingState, ErrorBanner } from "./OverviewPage";

export default function AlertsPage() {
  const [students, setStudents] = useState(null);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState(null);
  const [recsCache, setRecsCache] = useState({});

  useEffect(() => {
    api.getAlerts(100).then(setStudents).catch((e) => setError(e.message));
  }, []);

  async function toggleExpand(studentId) {
    if (expandedId === studentId) {
      setExpandedId(null);
      return;
    }
    setExpandedId(studentId);
    if (!recsCache[studentId]) {
      try {
        const recs = await api.getStudentRecommendations(studentId);
        setRecsCache((prev) => ({ ...prev, [studentId]: recs }));
      } catch (e) {
        setRecsCache((prev) => ({ ...prev, [studentId]: [] }));
      }
    }
  }

  if (error) return <ErrorBanner message={error} />;
  if (!students) return <LoadingState />;

  return (
    <div>
      <PageHeader
        title="Early Warning Alerts"
        subtitle={`${students.length} students flagged as High Risk, requiring counselor or faculty attention.`}
      />

      <div style={styles.banner}>
        🚨 {students.length} students currently require intervention. Click a
        student to view their personalized counseling plan.
      </div>

      <div style={styles.list}>
        {students.map((s) => {
          const isOpen = expandedId === s.student_id;
          const recs = recsCache[s.student_id];
          return (
            <div key={s.student_id} style={styles.card}>
              <button
                onClick={() => toggleExpand(s.student_id)}
                style={styles.cardHeader}
              >
                <div style={styles.cardHeaderLeft}>
                  <span style={styles.studentId}>{s.student_id}</span>
                  <RiskBadge tier={s.risk_tier} size="sm" />
                </div>
                <div style={styles.cardHeaderRight}>
                  <span style={styles.score}>{s.dropout_probability}%</span>
                  <span style={styles.chevron}>{isOpen ? "−" : "+"}</span>
                </div>
              </button>

              {isOpen && (
                <div style={styles.cardBody}>
                  <div style={styles.metricsRow}>
                    <Metric label="Attendance" value={`${s.attendance_pct}%`} />
                    <Metric label="Internal Marks" value={s.internal_marks_avg} />
                    <Metric label="Backlogs" value={s.backlogs} />
                    <Metric label="Fee Due" value={s.fee_due ? "Yes" : "No"} />
                  </div>

                  <div style={styles.recHeading}>Recommended Counseling Actions</div>
                  {!recs && <div style={styles.loadingRecs}>Loading recommendations...</div>}
                  {recs && recs.length === 0 && (
                    <div style={styles.loadingRecs}>No specific issue flagged.</div>
                  )}
                  {recs && recs.map((r, i) => (
                    <div key={i} style={styles.recItem}>
                      <div style={styles.recIssue}>{r.issue}</div>
                      <div style={styles.recAction}>{r.recommended_action}</div>
                    </div>
                  ))}

                  <Link to={`/students/${s.student_id}`} style={styles.fullProfileLink}>
                    View full student profile →
                  </Link>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div style={styles.metric}>
      <div style={styles.metricLabel}>{label}</div>
      <div style={styles.metricValue}>{value}</div>
    </div>
  );
}

const styles = {
  banner: {
    background: "var(--color-risk-high-bg)",
    color: "var(--color-risk-high)",
    padding: "var(--space-4) var(--space-5)",
    borderRadius: "var(--radius-md)",
    fontSize: 14,
    fontWeight: 600,
    marginBottom: "var(--space-5)",
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: "var(--space-3)",
  },
  card: {
    background: "var(--color-surface)",
    border: "1px solid var(--color-slate-100)",
    borderRadius: "var(--radius-md)",
    overflow: "hidden",
  },
  cardHeader: {
    width: "100%",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "var(--space-4) var(--space-5)",
    background: "transparent",
    border: "none",
    cursor: "pointer",
    textAlign: "left",
  },
  cardHeaderLeft: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-3)",
  },
  cardHeaderRight: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-4)",
  },
  studentId: {
    fontFamily: "monospace",
    fontWeight: 700,
    color: "var(--color-navy-950)",
    fontSize: 14,
  },
  score: {
    fontWeight: 700,
    color: "var(--color-risk-high)",
    fontSize: 15,
  },
  chevron: {
    fontSize: 18,
    color: "var(--color-slate-500)",
    width: 20,
    textAlign: "center",
  },
  cardBody: {
    padding: "0 var(--space-5) var(--space-5) var(--space-5)",
    borderTop: "1px solid var(--color-slate-100)",
  },
  metricsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "var(--space-3)",
    margin: "var(--space-4) 0",
  },
  metric: {
    background: "var(--color-bg)",
    borderRadius: "var(--radius-sm)",
    padding: "var(--space-3)",
  },
  metricLabel: {
    fontSize: 11,
    color: "var(--color-slate-500)",
    marginBottom: 2,
  },
  metricValue: {
    fontSize: 15,
    fontWeight: 700,
  },
  recHeading: {
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: "0.04em",
    textTransform: "uppercase",
    color: "var(--color-slate-500)",
    marginBottom: "var(--space-3)",
  },
  loadingRecs: {
    fontSize: 13,
    color: "var(--color-slate-500)",
    marginBottom: "var(--space-3)",
  },
  recItem: {
    background: "var(--color-risk-medium-bg)",
    borderRadius: "var(--radius-sm)",
    padding: "var(--space-3) var(--space-4)",
    marginBottom: "var(--space-2)",
  },
  recIssue: {
    fontSize: 13,
    fontWeight: 700,
    color: "var(--color-risk-medium)",
    marginBottom: 2,
  },
  recAction: {
    fontSize: 13,
    color: "var(--color-navy-800)",
    lineHeight: 1.5,
  },
  fullProfileLink: {
    display: "inline-block",
    marginTop: "var(--space-3)",
    fontSize: 13,
    fontWeight: 600,
    color: "var(--color-teal-700)",
  },
};
