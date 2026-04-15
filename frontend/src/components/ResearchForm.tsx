"use client";
import { useState } from "react";

interface Props {
  onSubmit: (query: string) => void;
  loading: boolean;
  showError?: boolean;
  onClearError?: () => void;
}

export function ResearchForm({ onSubmit, loading, showError, onClearError }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
  };

  return (
    <div>
      <textarea
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          onClearError?.();
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
        }}
        placeholder="e.g. What are the key advances in attention mechanisms for transformers?"
        rows={4}
        disabled={loading}
        style={{
          width: "100%",
          background: "var(--ivory)",
          border: showError 
            ? "1px solid var(--error)" 
            : "1px solid var(--border-warm)",
          borderRadius: "8px",
          padding: "16px",
          fontFamily: "system-ui, sans-serif",
          fontSize: "16px",
          lineHeight: "1.6",
          color: "var(--text-primary)",
          resize: "vertical",
          outline: "none",
          transition: "border-color 0.15s",
          opacity: loading ? 0.6 : 1,
        }}
        onFocus={(e) =>
          (e.currentTarget.style.borderColor = showError ? "var(--error)" : "var(--focus-blue)")
        }
        onBlur={(e) =>
          (e.currentTarget.style.borderColor = showError ? "var(--error)" : "var(--border-warm)")
        }
      />

      {/* Error State - Server Busy for EVERYTHING */}
      {showError && (
        <div
          style={{
            marginTop: "16px",
            padding: "20px 24px",
            borderRadius: "12px",
            background: "var(--ivory)",
            border: "1px solid var(--border-cream)",
            boxShadow: "rgba(0,0,0,0.04) 0px 2px 12px",
          }}
        >
          <h4
            style={{
              fontFamily: "Georgia, serif",
              fontSize: "18px",
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
              fontSize: "14px",
              lineHeight: "1.6",
              color: "var(--text-secondary)",
            }}
          >
            Our system is currently under high load. Please try again later.
          </p>
        </div>
      )}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: showError ? "20px" : "16px",
          flexWrap: "wrap",
          gap: "8px",
        }}
      >
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "12px",
            color: "var(--text-tertiary)",
          }}
        >
          ⌘ + Enter to submit
        </p>

        <button
          onClick={handleSubmit}
          disabled={loading || !query.trim()}
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "15px",
            fontWeight: 500,
            padding: "10px 24px",
            borderRadius: "12px",
            background:
              loading || !query.trim()
                ? "var(--warm-sand)"
                : "var(--terracotta)",
            color:
              loading || !query.trim()
                ? "var(--text-tertiary)"
                : "var(--ivory)",
            border: "none",
            cursor: loading || !query.trim() ? "not-allowed" : "pointer",
            boxShadow:
              loading || !query.trim()
                ? "0px 0px 0px 1px var(--ring-warm)"
                : "0px 0px 0px 1px var(--terracotta)",
          }}
        >
          {loading ? "Running agents..." : "Run Research →"}
        </button>
      </div>
    </div>
  );
}