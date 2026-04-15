"use client";
import type { JobStatus, IngestResult as IngestResultType } from "@/types/api";

interface Props {
  job: JobStatus;
}

export function IngestResult({ job }: Props) {
  const result = job.result as IngestResultType | undefined;

  const stats = [
    {
      label: "Pages processed",
      value: result?.pages_processed ?? "—",
      icon: "📄",
    },
    {
      label: "Chunks created",
      value: result?.chunks_created ?? "—",
      icon: "📚",
    },
    {
      label: "Embedding model",
      value: "gemini-embedding-2-preview",
      icon: "⚡",
    },
  ];

  return (
    <div>
      {/* Success header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          marginBottom: "24px",
        }}
      >
        <span
          style={{
            width: "28px",
            height: "28px",
            borderRadius: "50%",
            background: "var(--terracotta)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--ivory)",
            fontSize: "14px",
          }}
        >
          ✓
        </span>
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "16px",
            fontWeight: 500,
            color: "var(--text-primary)",
          }}
        >
          Ingestion complete
        </p>
      </div>

      {/* Stat cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "12px",
        }}
      >
        {stats.map((s) => (
          <div
            key={s.label}
            style={{
              background: "var(--ivory)",
              border: "1px solid var(--border-cream)",
              borderRadius: "8px",
              padding: "20px",
              boxShadow: "rgba(0,0,0,0.04) 0px 2px 12px",
            }}
          >
            <div style={{ fontSize: "20px", marginBottom: "8px" }}>{s.icon}</div>
            <p
              style={{
                fontFamily: "Georgia, serif",
                fontSize: "28px",
                fontWeight: 500,
                color: "var(--text-primary)",
                marginBottom: "4px",
              }}
            >
              {s.value}
            </p>
            <p
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "12px",
                color: "var(--text-tertiary)",
                textTransform: "uppercase",
                letterSpacing: "0.3px",
              }}
            >
              {s.label}
            </p>
          </div>
        ))}
      </div>

      {/* Timing */}
      {job.completed_at && job.created_at && (
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "13px",
            color: "var(--text-tertiary)",
            marginTop: "16px",
          }}
        >
          Completed in{" "}
          {Math.round(
            (new Date(job.completed_at).getTime() -
              new Date(job.created_at).getTime()) /
              1000
          )}
          s
        </p>
      )}
    </div>
  );
}
