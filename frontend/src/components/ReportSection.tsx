"use client";
import { useState } from "react";

interface Props {
  title: string;
  content: string;
  defaultOpen?: boolean;
}

export function ReportSection({ title, content, defaultOpen = false }: Props) {
  const [open, setOpen]     = useState(defaultOpen);
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      style={{
        background: "var(--ivory)",
        border: "1px solid var(--border-cream)",
        borderRadius: "8px",
        marginBottom: "12px",
        boxShadow: "rgba(0,0,0,0.05) 0px 4px 24px",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "20px 24px",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          textAlign: "left",
          outline: "none",
        }}
        onFocus={(e) =>
          (e.currentTarget.style.outline = "2px solid var(--focus-blue)")
        }
        onBlur={(e) => (e.currentTarget.style.outline = "none")}
      >
        <h3
          style={{
            fontFamily: "Georgia, serif",
            fontSize: "20px",
            fontWeight: 500,
            color: "var(--text-primary)",
            margin: 0,
          }}
        >
          {title}
        </h3>
        <span
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "18px",
            color: "var(--text-tertiary)",
            transform: open ? "rotate(180deg)" : "rotate(0)",
            transition: "transform 0.2s",
            display: "inline-block",
          }}
        >
          ↓
        </span>
      </button>

      {/* Body */}
      {open && (
        <div style={{ padding: "0 24px 24px" }}>
          <div
            style={{
              borderTop: "1px solid var(--border-cream)",
              paddingTop: "20px",
              marginBottom: "16px",
            }}
          >
            <p
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "16px",
                lineHeight: "1.7",
                color: "var(--text-secondary)",
                whiteSpace: "pre-wrap",
              }}
            >
              {content}
            </p>
          </div>

          {/* Copy button */}
          <button
            onClick={copy}
            style={{
              fontFamily: "system-ui, sans-serif",
              fontSize: "13px",
              padding: "6px 14px",
              borderRadius: "6px",
              background: "var(--warm-sand)",
              color: "#4d4c48",
              border: "none",
              cursor: "pointer",
              boxShadow: "0px 0px 0px 1px var(--ring-warm)",
            }}
          >
            {copied ? "Copied ✓" : "Copy section"}
          </button>
        </div>
      )}
    </div>
  );
}
