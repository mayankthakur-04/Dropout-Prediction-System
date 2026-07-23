const TIER_STYLES = {
  "High Risk": { bg: "var(--color-risk-high-bg)", fg: "var(--color-risk-high)" },
  "Medium Risk": { bg: "var(--color-risk-medium-bg)", fg: "var(--color-risk-medium)" },
  "Low Risk": { bg: "var(--color-risk-low-bg)", fg: "var(--color-risk-low)" },
};

export default function RiskBadge({ tier, size = "md" }) {
  const style = TIER_STYLES[tier] || { bg: "var(--color-slate-100)", fg: "var(--color-slate-500)" };
  const padding = size === "sm" ? "2px 10px" : "4px 14px";
  const fontSize = size === "sm" ? 11 : 13;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        background: style.bg,
        color: style.fg,
        padding,
        borderRadius: 999,
        fontSize,
        fontWeight: 600,
        whiteSpace: "nowrap",
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: style.fg,
          display: "inline-block",
        }}
      />
      {tier}
    </span>
  );
}
