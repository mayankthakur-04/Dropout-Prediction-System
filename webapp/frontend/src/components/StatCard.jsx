export default function StatCard({ label, value, accentColor, helpText }) {
  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-slate-100)",
        borderRadius: "var(--radius-md)",
        padding: "var(--space-5)",
        boxShadow: "var(--shadow-sm)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: 4,
          height: "100%",
          background: accentColor || "var(--color-teal-600)",
        }}
      />
      <div style={{ fontSize: 12, fontWeight: 600, color: "var(--color-slate-500)", letterSpacing: "0.02em" }}>
        {label}
      </div>
      <div
        style={{
          fontFamily: "var(--font-display)",
          fontSize: 32,
          fontWeight: 600,
          color: "var(--color-navy-950)",
          marginTop: 6,
        }}
      >
        {value}
      </div>
      {helpText && (
        <div style={{ fontSize: 12, color: "var(--color-slate-500)", marginTop: 4 }}>
          {helpText}
        </div>
      )}
    </div>
  );
}
