import Link from "next/link";

export default function Home() {
  return (
    <>
      {/* Hero — Parchment light section */}
      <section
        style={{
          background: "var(--parchment)",
          padding: "96px 40px 80px",
          textAlign: "center",
        }}
      >
        <div style={{ maxWidth: "680px", margin: "0 auto" }}>
          {/* Overline */}
          <p
            style={{
              fontFamily: "system-ui, sans-serif",
              fontSize: "10px",
              letterSpacing: "0.5px",
              textTransform: "uppercase",
              color: "var(--text-tertiary)",
              marginBottom: "28px",
            }}
          >
            Multi-Agent Research System
          </p>

          {/* H1 — Georgia serif, weight 500 */}
          <h1
            style={{
              fontSize: "clamp(32px, 5vw, 52px)",
              lineHeight: "1.2",
              marginBottom: "20px",
              color: "var(--text-primary)",
            }}
          >
            Research papers,
            <br />
            analysed by AI agents.
          </h1>

          {/* Subtitle */}
          <p
            style={{
              fontFamily: "system-ui, sans-serif",
              fontSize: "20px",
              lineHeight: "1.6",
              color: "var(--text-secondary)",
              marginBottom: "44px",
              maxWidth: "520px",
              margin: "0 auto 44px",
            }}
          >
            Upload arXiv papers. Five specialized Gemini agents read, critique,
            and synthesize the research into a structured report.
          </p>

          {/* CTAs */}
          <div
            style={{
              display: "flex",
              gap: "12px",
              justifyContent: "center",
              flexWrap: "wrap",
            }}
          >
            {/* Secondary — Warm Sand */}
            <Link
              href="/ingest"
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "16px",
                fontWeight: 500,
                padding: "10px 20px",
                borderRadius: "8px",
                background: "var(--warm-sand)",
                color: "#4d4c48",
                textDecoration: "none",
                boxShadow: "0px 0px 0px 1px var(--ring-warm)",
              }}
            >
              1 — Upload Papers
            </Link>

            {/* Primary — Terracotta */}
            <Link
              href="/research"
              style={{
                fontFamily: "system-ui, sans-serif",
                fontSize: "16px",
                fontWeight: 500,
                padding: "10px 20px",
                borderRadius: "12px",
                background: "var(--terracotta)",
                color: "var(--ivory)",
                textDecoration: "none",
                boxShadow: "0px 0px 0px 1px var(--terracotta)",
              }}
            >
              2 — Run Research →
            </Link>
          </div>
        </div>
      </section>

      {/* How it works — Near Black dark section */}
      <section
        style={{
          background: "var(--near-black)",
          padding: "80px 40px",
        }}
      >
        <div style={{ maxWidth: "800px", margin: "0 auto" }}>
          <h2
            style={{
              color: "var(--ivory)",
              fontSize: "36px",
              marginBottom: "40px",
              textAlign: "center",
            }}
          >
            Five agents. One report.
          </h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "16px",
            }}
          >
            {[
              { name: "Literature", desc: "Field evolution and key papers" },
              { name: "Methods",    desc: "Architecture and training strategies" },
              { name: "Results",    desc: "Benchmarks and performance claims" },
              { name: "Critique",   desc: "Limitations and open problems" },
              { name: "Synthesis",  desc: "Research gaps and future directions" },
            ].map((agent) => (
              <div
                key={agent.name}
                style={{
                  background: "var(--dark-surface)",
                  border: "1px solid var(--border-dark)",
                  borderRadius: "8px",
                  padding: "20px",
                }}
              >
                <p
                  style={{
                    fontFamily: "system-ui, sans-serif",
                    fontSize: "12px",
                    letterSpacing: "0.12px",
                    textTransform: "uppercase",
                    color: "var(--coral)",
                    marginBottom: "8px",
                  }}
                >
                  {agent.name}
                </p>
                <p
                  style={{
                    fontFamily: "system-ui, sans-serif",
                    fontSize: "15px",
                    color: "var(--text-warm-silver)",
                    lineHeight: "1.5",
                  }}
                >
                  {agent.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <section
        style={{
          background: "var(--parchment)",
          padding: "40px",
          textAlign: "center",
          borderTop: "1px solid var(--border-cream)",
        }}
      >
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: "13px",
            color: "var(--text-tertiary)",
          }}
        >
          Gemini 2.5 Flash · FAISS · FastAPI · Next.js ·{" "}
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "var(--coral)", textDecoration: "none" }}
          >
            GitHub →
          </a>
        </p>
      </section>
    </>
  );
}
