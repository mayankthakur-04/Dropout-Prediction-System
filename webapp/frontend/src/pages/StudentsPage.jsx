import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api/client";
import RiskBadge from "../components/RiskBadge";
import { PageHeader, LoadingState, ErrorBanner } from "./OverviewPage";

const TIER_OPTIONS = ["All", "High Risk", "Medium Risk", "Low Risk"];

export default function StudentsPage() {
  const [students, setStudents] = useState(null);
  const [error, setError] = useState("");
  const [tier, setTier] = useState("All");
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  const fetchStudents = useCallback(() => {
    api.getStudents({ riskTier: tier, search })
      .then(setStudents)
      .catch((e) => setError(e.message));
  }, [tier, search]);

  useEffect(() => {
    const timeout = setTimeout(fetchStudents, 250); // debounce search typing
    return () => clearTimeout(timeout);
  }, [fetchStudents]);

  return (
    <div>
      <PageHeader
        title="Risk Prediction Dashboard"
        subtitle="Search and filter all students by dropout risk score."
      />

      <div style={styles.toolbar}>
        <div style={styles.tierTabs}>
          {TIER_OPTIONS.map((t) => (
            <button
              key={t}
              onClick={() => setTier(t)}
              style={{
                ...styles.tierTab,
                ...(tier === t ? styles.tierTabActive : {}),
              }}
            >
              {t}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Search Student ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={styles.searchInput}
        />
      </div>

      {error && <ErrorBanner message={error} />}
      {!error && !students && <LoadingState />}

      {students && (
        <div style={styles.tableWrap}>
          <div style={styles.resultCount}>{students.length} students</div>
          <table>
            <thead>
              <tr style={styles.headerRow}>
                <th style={styles.th}>Student ID</th>
                <th style={styles.th}>Risk</th>
                <th style={styles.th}>Dropout %</th>
                <th style={styles.th}>Attendance</th>
                <th style={styles.th}>Internal Marks</th>
                <th style={styles.th}>Backlogs</th>
                <th style={styles.th}>Fee Due</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => (
                <tr
                  key={s.student_id}
                  style={styles.row}
                  onClick={() => navigate(`/students/${s.student_id}`)}
                >
                  <td style={styles.tdMono}>{s.student_id}</td>
                  <td style={styles.td}><RiskBadge tier={s.risk_tier} size="sm" /></td>
                  <td style={styles.td}>{s.dropout_probability}%</td>
                  <td style={styles.td}>{s.attendance_pct}%</td>
                  <td style={styles.td}>{s.internal_marks_avg}</td>
                  <td style={styles.td}>{s.backlogs}</td>
                  <td style={styles.td}>{s.fee_due ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {students.length === 0 && (
            <div style={styles.emptyState}>No students match this filter.</div>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  toolbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "var(--space-4)",
    flexWrap: "wrap",
    gap: "var(--space-3)",
  },
  tierTabs: {
    display: "flex",
    gap: 6,
    background: "var(--color-slate-100)",
    padding: 4,
    borderRadius: "var(--radius-sm)",
  },
  tierTab: {
    border: "none",
    background: "transparent",
    padding: "8px 14px",
    borderRadius: "var(--radius-sm)",
    fontSize: 13,
    fontWeight: 600,
    color: "var(--color-slate-500)",
    cursor: "pointer",
  },
  tierTabActive: {
    background: "var(--color-surface)",
    color: "var(--color-navy-950)",
    boxShadow: "var(--shadow-sm)",
  },
  searchInput: {
    padding: "9px 14px",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--color-slate-300)",
    fontSize: 14,
    minWidth: 240,
  },
  tableWrap: {
    background: "var(--color-surface)",
    border: "1px solid var(--color-slate-100)",
    borderRadius: "var(--radius-md)",
    overflow: "hidden",
  },
  resultCount: {
    padding: "var(--space-3) var(--space-4)",
    fontSize: 12,
    color: "var(--color-slate-500)",
    borderBottom: "1px solid var(--color-slate-100)",
  },
  headerRow: {
    background: "var(--color-bg)",
  },
  th: {
    textAlign: "left",
    padding: "10px var(--space-4)",
    fontSize: 12,
    fontWeight: 600,
    color: "var(--color-slate-500)",
    borderBottom: "1px solid var(--color-slate-100)",
  },
  row: {
    cursor: "pointer",
    transition: "background 0.1s",
  },
  td: {
    padding: "12px var(--space-4)",
    fontSize: 14,
    borderBottom: "1px solid var(--color-slate-100)",
  },
  tdMono: {
    padding: "12px var(--space-4)",
    fontSize: 13,
    fontFamily: "monospace",
    borderBottom: "1px solid var(--color-slate-100)",
    color: "var(--color-teal-700)",
    fontWeight: 600,
  },
  emptyState: {
    padding: "var(--space-7)",
    textAlign: "center",
    color: "var(--color-slate-500)",
    fontSize: 14,
  },
};
