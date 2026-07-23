import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { loginUser } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await loginUser(username, password);
      navigate("/");
    } catch (err) {
      setError(err.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.eyebrow}>Indian College Counseling Initiative</div>
        <h1 style={styles.title}>Dropout Prediction &amp;<br />Counseling System</h1>
        <p style={styles.subtitle}>
          Sign in to view student risk insights and counseling recommendations.
        </p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. faculty1"
              style={styles.input}
              autoFocus
              required
            />
          </label>

          <label style={styles.label}>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={styles.input}
              required
            />
          </label>

          {error && <div style={styles.error}>{error}</div>}

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div style={styles.demoBox}>
          <div style={styles.demoTitle}>Demo accounts</div>
          <div style={styles.demoRow}><span>Admin</span><span>admin / admin123</span></div>
          <div style={styles.demoRow}><span>Faculty</span><span>faculty1 / faculty123</span></div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(160deg, var(--color-navy-950) 0%, var(--color-navy-800) 55%, var(--color-teal-700) 130%)",
    padding: "var(--space-5)",
  },
  card: {
    width: "100%",
    maxWidth: 420,
    background: "var(--color-surface)",
    borderRadius: "var(--radius-lg)",
    boxShadow: "var(--shadow-md)",
    padding: "var(--space-7) var(--space-6)",
  },
  eyebrow: {
    fontFamily: "var(--font-body)",
    fontSize: 12,
    fontWeight: 600,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: "var(--color-teal-700)",
    marginBottom: "var(--space-3)",
  },
  title: {
    fontSize: 26,
    lineHeight: 1.25,
    marginBottom: "var(--space-3)",
  },
  subtitle: {
    color: "var(--color-slate-500)",
    fontSize: 14,
    marginBottom: "var(--space-6)",
    lineHeight: 1.5,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "var(--space-4)",
  },
  label: {
    display: "flex",
    flexDirection: "column",
    gap: "var(--space-2)",
    fontSize: 13,
    fontWeight: 600,
    color: "var(--color-navy-800)",
  },
  input: {
    fontFamily: "var(--font-body)",
    fontSize: 15,
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--color-slate-300)",
    background: "var(--color-bg)",
    color: "var(--color-navy-950)",
  },
  error: {
    background: "var(--color-risk-high-bg)",
    color: "var(--color-risk-high)",
    fontSize: 13,
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
  },
  button: {
    marginTop: "var(--space-2)",
    background: "var(--color-teal-600)",
    color: "white",
    border: "none",
    padding: "12px 16px",
    borderRadius: "var(--radius-sm)",
    fontSize: 15,
    fontWeight: 600,
    cursor: "pointer",
  },
  demoBox: {
    marginTop: "var(--space-6)",
    paddingTop: "var(--space-5)",
    borderTop: "1px solid var(--color-slate-100)",
  },
  demoTitle: {
    fontSize: 11,
    fontWeight: 700,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    color: "var(--color-slate-500)",
    marginBottom: "var(--space-2)",
  },
  demoRow: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: 13,
    color: "var(--color-navy-800)",
    padding: "4px 0",
    fontFamily: "monospace",
  },
};
