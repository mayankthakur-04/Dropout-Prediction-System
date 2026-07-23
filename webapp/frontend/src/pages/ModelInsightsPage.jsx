import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import * as api from "../api/client";
import Card from "../components/Card";
import StatCard from "../components/StatCard";
import { PageHeader, LoadingState, ErrorBanner } from "./OverviewPage";

export default function ModelInsightsPage() {
  const [metrics, setMetrics] = useState(null);
  const [importance, setImportance] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getModelMetrics(), api.getFeatureImportance()])
      .then(([m, fi]) => {
        setMetrics(m);
        setImportance(
          fi
            .slice()
            .sort((a, b) => b.importance - a.importance)
            .slice(0, 10)
            .reverse()
            .map((f) => ({ ...f, importance: Number((f.importance * 100).toFixed(1)) }))
        );
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorBanner message={error} />;
  if (!metrics || !importance) return <LoadingState />;

  const rf = metrics.random_forest_tuned_threshold;
  const lr = metrics.logistic_regression;

  return (
    <div>
      <PageHeader
        title="Model Insights"
        subtitle="Performance metrics and explainability for the trained dropout prediction model."
      />

      <Card title="Random Forest (Main Model)" subtitle={`Classification threshold tuned to ${metrics.tuned_threshold_value} to prioritize recall`} style={{ marginBottom: "var(--space-5)" }}>
        <div style={styles.metricGrid}>
          <StatCard label="Accuracy" value={rf.accuracy.toFixed(2)} />
          <StatCard label="Precision" value={rf.precision.toFixed(2)} />
          <StatCard label="Recall" value={rf.recall.toFixed(2)} accentColor="var(--color-teal-600)" />
          <StatCard label="F1-Score" value={rf.f1.toFixed(2)} />
          <StatCard label="ROC-AUC" value={rf.auc.toFixed(2)} />
        </div>
      </Card>

      <Card title="Logistic Regression (Baseline)" subtitle="For comparison — Random Forest outperforms this baseline" style={{ marginBottom: "var(--space-5)" }}>
        <div style={styles.metricGrid}>
          <StatCard label="Accuracy" value={lr.accuracy.toFixed(2)} />
          <StatCard label="Precision" value={lr.precision.toFixed(2)} />
          <StatCard label="Recall" value={lr.recall.toFixed(2)} />
          <StatCard label="F1-Score" value={lr.f1.toFixed(2)} />
          <StatCard label="ROC-AUC" value={lr.auc.toFixed(2)} />
        </div>
      </Card>

      <Card
        title="Top Factors Contributing to Dropout"
        subtitle={`Feature importance from Random Forest, trained on ${metrics.dataset_size.toLocaleString()} students (${metrics.dropout_rate_pct}% dropout rate)`}
      >
        <ResponsiveContainer width="100%" height={380}>
          <BarChart data={importance} layout="vertical" margin={{ left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" unit="%" fontSize={12} />
            <YAxis dataKey="feature" type="category" width={170} fontSize={12} />
            <Tooltip formatter={(v) => `${v}%`} />
            <Bar dataKey="importance" fill="var(--color-teal-600)" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}

const styles = {
  metricGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gap: "var(--space-3)",
  },
};
