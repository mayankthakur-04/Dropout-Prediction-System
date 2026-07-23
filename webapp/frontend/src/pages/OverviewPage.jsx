import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import * as api from "../api/client";
import StatCard from "../components/StatCard";
import Card from "../components/Card";

const TIER_COLORS = {
  "High Risk": "#B0473F",
  "Medium Risk": "#C7872E",
  "Low Risk": "#4C8C57",
};

export default function OverviewPage() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getOverview().then(setStats).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorBanner message={error} />;
  if (!stats) return <LoadingState />;

  const pieData = [
    { name: "High Risk", value: stats.high_risk_count },
    { name: "Medium Risk", value: stats.medium_risk_count },
    { name: "Low Risk", value: stats.low_risk_count },
  ];

  return (
    <div>
      <PageHeader
        title="Institution Overview"
        subtitle="A snapshot of student dropout risk across the institution."
      />

      <div style={styles.statGrid}>
        <StatCard
          label="Total Students"
          value={stats.total_students.toLocaleString()}
          accentColor="var(--color-navy-700)"
        />
        <StatCard
          label="High Risk"
          value={stats.high_risk_count.toLocaleString()}
          accentColor="var(--color-risk-high)"
          helpText={`${((stats.high_risk_count / stats.total_students) * 100).toFixed(1)}% of students`}
        />
        <StatCard
          label="Medium Risk"
          value={stats.medium_risk_count.toLocaleString()}
          accentColor="var(--color-risk-medium)"
          helpText={`${((stats.medium_risk_count / stats.total_students) * 100).toFixed(1)}% of students`}
        />
        <StatCard
          label="Average Dropout Risk"
          value={`${stats.avg_dropout_probability}%`}
          accentColor="var(--color-teal-600)"
        />
      </div>

      <div style={styles.chartRow}>
        <Card title="Risk Tier Distribution" subtitle="Share of students in each risk category">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                innerRadius={70}
                outerRadius={100}
                paddingAngle={2}
              >
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={TIER_COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card title="What this means" subtitle="Reading the risk distribution">
          <p style={styles.bodyText}>
            Students are grouped into three tiers based on the dropout
            probability score produced by the trained Random Forest model.
          </p>
          <ul style={styles.list}>
            <li><strong>High Risk</strong> (≥55%): flagged for immediate counselor attention.</li>
            <li><strong>Medium Risk</strong> (30–55%): worth monitoring, early intervention helpful.</li>
            <li><strong>Low Risk</strong> (&lt;30%): no immediate action needed.</li>
          </ul>
          <p style={styles.bodyText}>
            See the <strong>Alerts</strong> page for a ready-to-act list of
            High Risk students with personalized counseling recommendations.
          </p>
        </Card>
      </div>
    </div>
  );
}

export function PageHeader({ title, subtitle }) {
  return (
    <div style={{ marginBottom: "var(--space-6)" }}>
      <h1 style={{ fontSize: 24, marginBottom: 6 }}>{title}</h1>
      {subtitle && <p style={{ color: "var(--color-slate-500)", fontSize: 14 }}>{subtitle}</p>}
    </div>
  );
}

export function LoadingState({ label = "Loading..." }) {
  return (
    <div style={{ padding: "var(--space-7)", textAlign: "center", color: "var(--color-slate-500)" }}>
      {label}
    </div>
  );
}

export function ErrorBanner({ message }) {
  return (
    <div
      style={{
        background: "var(--color-risk-high-bg)",
        color: "var(--color-risk-high)",
        padding: "var(--space-4)",
        borderRadius: "var(--radius-sm)",
        fontSize: 14,
      }}
    >
      {message}
    </div>
  );
}

const styles = {
  statGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "var(--space-4)",
    marginBottom: "var(--space-6)",
  },
  chartRow: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "var(--space-5)",
  },
  bodyText: {
    fontSize: 14,
    color: "var(--color-navy-800)",
    lineHeight: 1.6,
    marginBottom: "var(--space-3)",
  },
  list: {
    fontSize: 14,
    color: "var(--color-navy-800)",
    lineHeight: 1.7,
    paddingLeft: "var(--space-5)",
    marginBottom: "var(--space-3)",
  },
};
