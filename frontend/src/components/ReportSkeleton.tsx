export function ReportSkeleton() {
  const shimmerStyle: React.CSSProperties = {
    background:
      "linear-gradient(90deg, var(--warm-sand) 25%, var(--border-warm) 50%, var(--warm-sand) 75%)",
    backgroundSize: "800px 100%",
    animation: "shimmer 1.4s infinite linear",
    borderRadius: "4px",
  };

  return (
    <div style={{ margin: "24px 0" }}>
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          style={{
            background: "var(--ivory)",
            border: "1px solid var(--border-cream)",
            borderRadius: "8px",
            padding: "20px 24px",
            marginBottom: "12px",
            boxShadow: "rgba(0,0,0,0.03) 0px 2px 8px",
          }}
        >
          {/* Title placeholder */}
          <div
            style={{
              ...shimmerStyle,
              height: "22px",
              width: `${40 + i * 10}%`,
              marginBottom: "16px",
            }}
          />
          {/* Lines */}
          {[100, 90, 80].map((w, j) => (
            <div
              key={j}
              style={{
                ...shimmerStyle,
                height: "14px",
                width: `${w}%`,
                marginBottom: "8px",
              }}
            />
          ))}
        </div>
      ))}

      <style>{`
        @keyframes shimmer {
          0%   { background-position: -400px 0; }
          100% { background-position:  800px 0; }
        }
      `}</style>
    </div>
  );
}
