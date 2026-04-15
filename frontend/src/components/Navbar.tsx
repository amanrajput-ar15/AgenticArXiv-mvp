"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const [chunks, setChunks] = useState<number | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const res  = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
        const data = await res.json();
        setChunks(data.total_chunks ?? 0);
      } catch {
        setChunks(null);
      }
    };
    check();
    const iv = setInterval(check, 30_000);
    return () => clearInterval(iv);
  }, []);

  const dotColor =
    chunks === null ? "#87867f" : chunks > 0 ? "#15803d" : "#d97757";

  return (
    <nav
      style={{
        position: "fixed",
        top: 0,
        width: "100%",
        zIndex: 50,
        background: "var(--parchment)",
        borderBottom: "1px solid var(--border-cream)",
        height: "52px",
        display: "flex",
        alignItems: "center",
        padding: "0 40px",
        justifyContent: "space-between",
      }}
    >
      {/* Left — logo + nav links */}
      <div style={{ display: "flex", alignItems: "center", gap: "32px" }}>
        <Link
          href="/"
          style={{
            fontFamily: "Georgia, serif",
            fontSize: "17px",
            fontWeight: 500,
            color: "var(--text-primary)",
            textDecoration: "none",
          }}
        >
          AgenticArXiv
        </Link>

        <div style={{ display: "flex", gap: "4px" }}>
          {[
            { href: "/ingest",   label: "Ingest" },
            { href: "/research", label: "Research" },
          ].map((l) => (
            <Link
              key={l.href}
              href={l.href}
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "15px",
                padding: "6px 12px",
                borderRadius: "8px",
                color:
                  pathname === l.href
                    ? "var(--text-primary)"
                    : "var(--text-secondary)",
                background:
                  pathname === l.href ? "var(--warm-sand)" : "transparent",
                textDecoration: "none",
                transition: "background 0.15s, color 0.15s",
              }}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </div>

      {/* Right — status pill */}
      <div
        style={{
          fontFamily: "system-ui, sans-serif",
          fontSize: "12px",
          letterSpacing: "0.12px",
          display: "flex",
          alignItems: "center",
          gap: "6px",
          padding: "4px 12px",
          borderRadius: "24px",
          background: "var(--warm-sand)",
          color: "var(--text-secondary)",
          boxShadow: "0px 0px 0px 1px var(--ring-warm)",
        }}
      >
        <span
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            background: dotColor,
            display: "inline-block",
          }}
        />
        {chunks === null
          ? "Connecting..."
          : chunks === 0
          ? "No papers indexed"
          : `${chunks} chunks indexed`}
      </div>
    </nav>
  );
}
