import { NavLink, useNavigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: "◧" },
  { to: "/students", label: "Risk Dashboard", icon: "☰" },
  { to: "/alerts", label: "Alerts", icon: "▲" },
  { to: "/calculator", label: "Risk Calculator", icon: "✎" },
  { to: "/model", label: "Model Insights", icon: "◎" },
];

export default function DashboardLayout() {
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logoutUser();
    navigate("/login");
  }

  const navItems = user?.role === "admin"
    ? [...NAV_ITEMS, { to: "/admin", label: "Manage Users", icon: "⚙" }]
    : NAV_ITEMS;

  return (
    <div style={styles.shell}>
      <aside style={styles.sidebar}>
        <div style={styles.brand}>
          <div style={styles.brandMark}>DP</div>
          <div>
            <div style={styles.brandTitle}>Dropout Prediction</div>
            <div style={styles.brandSubtitle}>&amp; Counseling System</div>
          </div>
        </div>

        <nav style={styles.nav}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => ({
                ...styles.navLink,
                ...(isActive ? styles.navLinkActive : {}),
              })}
            >
              <span style={styles.navIcon}>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div style={styles.sidebarFooter}>
          <div style={styles.userBlock}>
            <div style={styles.avatar}>
              {user?.full_name ? user.full_name.charAt(0) : "?"}
            </div>
            <div>
              <div style={styles.userName}>{user?.full_name}</div>
              <div style={styles.userRole}>{user?.role}</div>
            </div>
          </div>
          <button onClick={handleLogout} style={styles.logoutButton}>
            Sign out
          </button>
        </div>
      </aside>

      <main style={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}

const styles = {
  shell: {
    display: "flex",
    minHeight: "100vh",
  },
  sidebar: {
    width: 260,
    flexShrink: 0,
    background: "var(--color-navy-950)",
    color: "var(--color-slate-100)",
    display: "flex",
    flexDirection: "column",
    padding: "var(--space-5) var(--space-4)",
    position: "sticky",
    top: 0,
    height: "100vh",
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-3)",
    padding: "0 var(--space-2) var(--space-6) var(--space-2)",
    borderBottom: "1px solid rgba(255,255,255,0.08)",
    marginBottom: "var(--space-5)",
  },
  brandMark: {
    width: 36,
    height: 36,
    borderRadius: "var(--radius-sm)",
    background: "var(--color-teal-600)",
    color: "white",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    fontSize: 14,
    flexShrink: 0,
  },
  brandTitle: {
    fontFamily: "var(--font-display)",
    fontSize: 14,
    fontWeight: 600,
    color: "white",
    lineHeight: 1.3,
  },
  brandSubtitle: {
    fontSize: 11,
    color: "var(--color-slate-300)",
  },
  nav: {
    display: "flex",
    flexDirection: "column",
    gap: "var(--space-1)",
    flex: 1,
  },
  navLink: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-3)",
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    color: "var(--color-slate-300)",
    fontSize: 14,
    fontWeight: 500,
    textDecoration: "none",
  },
  navLinkActive: {
    background: "rgba(45, 140, 140, 0.18)",
    color: "white",
  },
  navIcon: {
    width: 18,
    textAlign: "center",
    opacity: 0.85,
  },
  sidebarFooter: {
    borderTop: "1px solid rgba(255,255,255,0.08)",
    paddingTop: "var(--space-4)",
    display: "flex",
    flexDirection: "column",
    gap: "var(--space-3)",
  },
  userBlock: {
    display: "flex",
    alignItems: "center",
    gap: "var(--space-3)",
    padding: "0 var(--space-2)",
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: "50%",
    background: "var(--color-teal-700)",
    color: "white",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 600,
    fontSize: 13,
    flexShrink: 0,
  },
  userName: {
    fontSize: 13,
    fontWeight: 600,
    color: "white",
  },
  userRole: {
    fontSize: 11,
    color: "var(--color-slate-300)",
    textTransform: "capitalize",
  },
  logoutButton: {
    background: "transparent",
    border: "1px solid rgba(255,255,255,0.15)",
    color: "var(--color-slate-100)",
    padding: "8px 12px",
    borderRadius: "var(--radius-sm)",
    fontSize: 13,
    cursor: "pointer",
  },
  main: {
    flex: 1,
    padding: "var(--space-6) var(--space-7)",
    maxWidth: 1280,
  },
};
