"use client";
import { useState } from "react";
import Link from "next/link";
import { IngestForm } from "@/components/IngestForm";
import { IngestResult } from "@/components/IngestResult";
import type { JobStatus } from "@/types/api";

export default function IngestPage() {
  const [result, setResult] = useState<JobStatus | null>(null);

  return (
    <div
      style={{
        background: "var(--parchment)",
        minHeight: "calc(100vh - 52px)",
        padding: "60px 40px",
      }}
    >
      <div style={{ maxWidth: "600px", margin: "0 auto" }}>
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "10px",
            letterSpacing: "0.5px",
            textTransform: "uppercase",
            color: "var(--text-tertiary)",
            marginBottom: "12px",
          }}
        >
          Step 1
        </p>
        <h1
          style={{
            fontSize: "clamp(28px, 4vw, 40px)",
            marginBottom: "8px",
            color: "var(--text-primary)",
          }}
        >
          Ingest Papers
        </h1>
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "17px",
            color: "var(--text-secondary)",
            marginBottom: "40px",
            lineHeight: "1.6",
          }}
        >
          Upload an arXiv PDF. Gemini Vision extracts the text page-by-page,
          preserving multi-column layouts, tables, and equations.
        </p>

        {!result ? (
          <IngestForm onComplete={setResult} />
        ) : (
          <div>
            <IngestResult job={result} />
            <div
              style={{
                marginTop: "32px",
                display: "flex",
                gap: "12px",
                flexWrap: "wrap",
              }}
            >
              <button
                onClick={() => setResult(null)}
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontSize: "15px",
                  padding: "10px 20px",
                  borderRadius: "8px",
                  background: "var(--warm-sand)",
                  color: "#4d4c48",
                  border: "none",
                  cursor: "pointer",
                  boxShadow: "0px 0px 0px 1px var(--ring-warm)",
                }}
              >
                Upload another
              </button>
              <Link
                href="/research"
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontSize: "15px",
                  fontWeight: 500,
                  padding: "10px 20px",
                  borderRadius: "12px",
                  background: "var(--terracotta)",
                  color: "var(--ivory)",
                  textDecoration: "none",
                  boxShadow: "0px 0px 0px 1px var(--terracotta)",
                }}
              >
                Run Research →
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
