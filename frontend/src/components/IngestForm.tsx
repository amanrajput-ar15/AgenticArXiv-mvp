"use client";
import { useRef, useState } from "react";
import { uploadPDF, pollUntilDone } from "@/lib/api";
import type { JobStatus } from "@/types/api";

interface Props {
  onComplete: (job: JobStatus) => void;
}

export function IngestForm({ onComplete }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [showError, setShowError] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    if (!f.name.toLowerCase().endsWith(".pdf")) {
      setShowError(true);
      return;
    }
    setShowError(false);
    setFile(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setShowError(false);
    setStatusMsg("Uploading...");

    try {
      const { job_id } = await uploadPDF(file);
      setStatusMsg("Processing...");

      await pollUntilDone(job_id, () => {});

      const done = await pollUntilDone(job_id, () => {});
      onComplete(done);
    } catch {
      setShowError(true);
      setStatusMsg("");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setShowError(false);
    setStatusMsg("");
  };

  return (
    <div>
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !loading && inputRef.current?.click()}
        style={{
          background: dragOver ? "#fdf0eb" : "var(--ivory)",
          border: dragOver
            ? "2px dashed var(--terracotta)"
            : "1px dashed var(--border-warm)",
          borderRadius: "12px",
          padding: "48px 24px",
          textAlign: "center",
          cursor: loading ? "not-allowed" : "pointer",
          transition: "border-color 0.15s, background 0.15s",
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
          }}
        />

        <div
          style={{
            width: "48px",
            height: "48px",
            borderRadius: "50%",
            background: "var(--warm-sand)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 16px",
            fontSize: "22px",
          }}
        >
          ↑
        </div>

        {file ? (
          <div>
            <p
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "16px",
                fontWeight: 500,
                color: "var(--text-primary)",
                marginBottom: "4px",
              }}
            >
              {file.name}
            </p>
            <p
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "13px",
                color: "var(--text-tertiary)",
              }}
            >
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div>
            <p
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "16px",
                color: "var(--text-secondary)",
                marginBottom: "6px",
              }}
            >
              Drag and drop a PDF here
            </p>
            <p
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "13px",
                color: "var(--text-tertiary)",
              }}
            >
              or click to browse — max 50MB
            </p>
          </div>
        )}
      </div>

      {/* Error State - Server Busy for EVERYTHING */}
      {showError && (
        <div
          style={{
            marginTop: "20px",
            padding: "24px",
            borderRadius: "12px",
            background: "var(--ivory)",
            border: "1px solid var(--border-cream)",
            boxShadow: "rgba(0,0,0,0.04) 0px 2px 12px",
          }}
        >
          <h4
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "20px",
              fontWeight: 500,
              color: "var(--text-primary)",
              marginBottom: "12px",
            }}
          >
            Server Busy
          </h4>
          
          <p
            style={{
              fontFamily: "system-ui, sans-serif",
              fontSize: "15px",
              lineHeight: "1.6",
              color: "var(--text-secondary)",
              marginBottom: "20px",
            }}
          >
            Our system is currently under high load. Please try again later.
          </p>

          <button
            onClick={reset}
            style={{
              fontFamily: "system-ui, sans-serif",
              fontSize: "15px",
              fontWeight: 500,
              padding: "10px 20px",
              borderRadius: "8px",
              background: "var(--warm-sand)",
              color: "#4d4c48",
              border: "none",
              cursor: "pointer",
              boxShadow: "0px 0px 0px 1px var(--ring-warm)",
            }}
          >
            Try Again
          </button>
        </div>
      )}

      {/* Status */}
      {statusMsg && !showError && (
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "14px",
            color: "var(--text-secondary)",
            marginTop: "20px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          {loading && (
            <span
              style={{
                display: "inline-block",
                width: "14px",
                height: "14px",
                border: "2px solid var(--border-warm)",
                borderTopColor: "var(--terracotta)",
                borderRadius: "50%",
                animation: "spin 0.8s linear infinite",
              }}
            />
          )}
          {statusMsg}
        </p>
      )}

      {/* Submit button */}
      {file && !loading && !showError && (
        <button
          onClick={handleSubmit}
          style={{
            marginTop: "24px",
            fontFamily: "system-ui, sans-serif",
            fontSize: "15px",
            fontWeight: 500,
            padding: "12px 24px",
            borderRadius: "12px",
            background: "var(--terracotta)",
            color: "var(--ivory)",
            border: "none",
            cursor: "pointer",
            boxShadow: "0px 0px 0px 1px var(--terracotta)",
            width: "100%",
          }}
        >
          Ingest Paper →
        </button>
      )}

      {/* Loading state */}
      {loading && (
        <div
          style={{
            marginTop: "24px",
            padding: "12px 24px",
            borderRadius: "12px",
            background: "var(--warm-sand)",
            color: "var(--text-tertiary)",
            fontFamily: "system-ui, sans-serif",
            fontSize: "15px",
            textAlign: "center",
            boxShadow: "0px 0px 0px 1px var(--ring-warm)",
          }}
        >
          Processing...
        </div>
      )}

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}