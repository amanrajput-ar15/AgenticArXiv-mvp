const AGENTS = [
  "literature",
  "methods",
  "results",
  "critique",
  "synthesis",
] as const;

interface Props {
  completed: string[];
}

export function AgentProgress({ completed }: Props) {
  return (
    <div
      style={{
        background: "var(--dark-surface)",
        border: "1px solid var(--border-dark)",
        borderRadius: "12px",
        padding: "24px",
        margin: "24px 0",
      }}
    >
      <p
        style={{
          fontFamily: "system-ui, sans-serif",
          fontSize: "12px",
          letterSpacing: "0.12px",
          textTransform: "uppercase",
          color: "var(--text-tertiary)",
          marginBottom: "16px",
        }}
      >
        Running agents...
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {AGENTS.map((name, i) => {
          const done    = completed.includes(name);
          const current = !done && i === completed.length;

          return (
            <div
              key={name}
              style={{ display: "flex", alignItems: "center", gap: "12px" }}
            >
              {/* Indicator circle */}
              <span
                style={{
                  width: "20px",
                  height: "20px",
                  borderRadius: "50%",
                  flexShrink: 0,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "11px",
                  fontFamily: "system-ui, sans-serif",
                  border: done
                    ? "1px solid var(--terracotta)"
                    : current
                    ? "1px solid var(--coral)"
                    : "1px solid var(--border-dark)",
                  background: done
                    ? "var(--terracotta)"
                    : "transparent",
                  color: done
                    ? "var(--ivory)"
                    : current
                    ? "var(--coral)"
                    : "var(--text-tertiary)",
                }}
              >
                {done ? "✓" : i + 1}
              </span>

              {/* Agent name */}
              <span
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontSize: "14px",
                  textTransform: "capitalize",
                  color: done
                    ? "var(--text-warm-silver)"
                    : current
                    ? "var(--ivory)"
                    : "var(--text-tertiary)",
                }}
              >
                {name}
              </span>

              {/* Running pulse */}
              {current && (
                <span
                  style={{
                    fontFamily: "system-ui, sans-serif",
                    fontSize: "12px",
                    color: "var(--coral)",
                    animation: "pulse 1.5s ease-in-out infinite",
                  }}
                >
                  running...
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
