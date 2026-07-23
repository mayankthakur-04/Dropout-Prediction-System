export default function Card({ title, subtitle, children, style }) {
  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-slate-100)",
        borderRadius: "var(--radius-md)",
        padding: "var(--space-5)",
        boxShadow: "var(--shadow-sm)",
        ...style,
      }}
    >
      {title && (
        <div style={{ marginBottom: "var(--space-4)" }}>
          <h3 style={{ fontSize: 16, fontWeight: 600 }}>{title}</h3>
          {subtitle && (
            <p style={{ fontSize: 13, color: "var(--color-slate-500)", marginTop: 4 }}>
              {subtitle}
            </p>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
