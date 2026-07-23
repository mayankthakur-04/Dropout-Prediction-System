import { useEffect, useState } from "react";
import * as api from "../api/client";
import Card from "../components/Card";
import { PageHeader, LoadingState, ErrorBanner } from "./OverviewPage";

export default function AdminUsersPage() {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getAdminUsers().then(setUsers).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorBanner message={error} />;
  if (!users) return <LoadingState />;

  return (
    <div>
      <PageHeader
        title="Manage Users"
        subtitle="Faculty and admin accounts with access to this system."
      />

      <Card>
        <table>
          <thead>
            <tr>
              <th style={styles.th}>Full Name</th>
              <th style={styles.th}>Username</th>
              <th style={styles.th}>Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.username}>
                <td style={styles.td}>{u.full_name}</td>
                <td style={styles.tdMono}>{u.username}</td>
                <td style={styles.td}>
                  <span style={styles.roleBadge}>{u.role}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p style={styles.note}>
          Accounts are currently configured directly in the backend
          (<code>auth.py</code>) for this demo system. A production version
          would add account creation, password resets, and a real database
          here.
        </p>
      </Card>
    </div>
  );
}

const styles = {
  th: {
    textAlign: "left",
    padding: "10px var(--space-2)",
    fontSize: 12,
    fontWeight: 600,
    color: "var(--color-slate-500)",
    borderBottom: "1px solid var(--color-slate-100)",
  },
  td: {
    padding: "12px var(--space-2)",
    fontSize: 14,
    borderBottom: "1px solid var(--color-slate-100)",
  },
  tdMono: {
    padding: "12px var(--space-2)",
    fontSize: 13,
    fontFamily: "monospace",
    borderBottom: "1px solid var(--color-slate-100)",
  },
  roleBadge: {
    background: "var(--color-teal-100)",
    color: "var(--color-teal-700)",
    padding: "3px 10px",
    borderRadius: 999,
    fontSize: 12,
    fontWeight: 600,
    textTransform: "capitalize",
  },
  note: {
    fontSize: 12,
    color: "var(--color-slate-500)",
    marginTop: "var(--space-5)",
    lineHeight: 1.6,
  },
};
