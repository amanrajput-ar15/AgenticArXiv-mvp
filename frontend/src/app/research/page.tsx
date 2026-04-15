"use client";
import { useState } from "react";
import { ResearchForm } from "@/components/ResearchForm";
import { AgentProgress } from "@/components/AgentProgress";
import { ReportSection } from "@/components/ReportSection";
import { ReportSkeleton } from "@/components/ReportSkeleton";
import { SourceCard } from "@/components/SourceCard";
import { conductResearch, pollUntilDone, clearVectorStore } from "@/lib/api";
import type { JobStatus, ResearchReport } from "@/types/api";

type Phase = "idle" | "running" | "done" | "error";

export default function ResearchPage() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [agentsDone, setAgentsDone] = useState<string[]>([]);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [showError, setShowError] = useState(false);
  const [clearing, setClearing] = useState(false);

  const handleSubmit = async (query: string) => {
    setPhase("running");
    setAgentsDone([]);
    setReport(null);
    setShowError(false);

    try {
      const { job_id } = await conductResearch(query);

      const done = await pollUntilDone(job_id, (job: JobStatus) => {
        if (job.agents_completed) {
          setAgentsDone([...job.agents_completed]);
        }
      });

      // Check if result is valid
      if (!done.result || !(done.result as ResearchReport).literature_review) {
        throw new Error("Invalid result");
      }

      setReport(done.result as ResearchReport);
      setPhase("done");
    } catch {
      // ANY error -> show server busy
      setShowError(true);
      setPhase("error");
    }
  };

  const handleClear = async () => {
    if (!confirm("Clear all indexed papers? This cannot be undone.")) return;
    setClearing(true);
    try {
      await clearVectorStore();
      window.location.reload();
    } catch {
      alert("Failed to clear");
    } finally {
      setClearing(false);
    }
  };

  const downloadReport = () => {
    if (!report) return;
    const md = [
      `# Research Report\n\n**Query:** ${report.query}\n`,
      `## Literature Review\n\n${report.literature_review}`,
      `## Methods Analysis\n\n${report.methods_analysis}`,
      `## Results Analysis\n\n${report.results_analysis}`,
      `## Critique\n\n${report.critique}`,
      `## Synthesis\n\n${report.synthesis}`,
      `## Sources\n\n${(report.sources ?? [])
        .map(
          (s) =>
            `- ${s.title} (${s.published?.slice(0, 4)}) — https://arxiv.org/abs/${s.paper_id}`
        )
        .join("\n")}`,
    ].join("\n\n---\n\n");

    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "research-report.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      style={{
        background: "var(--parchment)",
        minHeight: "calc(100vh - 52px)",
        padding: "60px 40px",
      }}
    >
      <div style={{ maxWidth: "720px", margin: "0 auto" }}>
        {/* Header */}
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
          Step 2
        </p>
        <h1
          style={{
            fontSize: "clamp(28px, 4vw, 40px)",
            marginBottom: "8px",
          }}
        >
          Run Research
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
          Ask a research question. Five specialized Gemini agents will analyse
          your indexed papers and produce a structured report.
        </p>

        {/* Query form */}
        <ResearchForm 
          onSubmit={handleSubmit} 
          loading={phase === "running"} 
          showError={showError}
          onClearError={() => setShowError(false)}
        />

        {/* Agent progress */}
        {phase === "running" && (
          <>
            <AgentProgress completed={agentsDone} />
            <ReportSkeleton />
          </>
        )}

        {/* Report */}
        {phase === "done" && report && (
          <div style={{ marginTop: "40px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "24px",
                flexWrap: "wrap",
                gap: "12px",
              }}
            >
              <h2 style={{ fontSize: "24px" }}>Report</h2>
              <button
                onClick={downloadReport}
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontSize: "13px",
                  padding: "7px 14px",
                  borderRadius: "6px",
                  background: "var(--warm-sand)",
                  color: "#4d4c48",
                  border: "none",
                  cursor: "pointer",
                  boxShadow: "0px 0px 0px 1px var(--ring-warm)",
                }}
              >
                Download .md
              </button>
            </div>

            <ReportSection title="Literature Review" content={report.literature_review} defaultOpen />
            <ReportSection title="Methods Analysis" content={report.methods_analysis} />
            <ReportSection title="Results Analysis" content={report.results_analysis} />
            <ReportSection title="Critique" content={report.critique} />
            <ReportSection title="Synthesis" content={report.synthesis} defaultOpen />

            {/* Sources */}
            {(report.sources ?? []).length > 0 && (
              <div
                style={{
                  background: "var(--ivory)",
                  border: "1px solid var(--border-cream)",
                  borderRadius: "8px",
                  padding: "20px 24px",
                  marginTop: "12px",
                  boxShadow: "rgba(0,0,0,0.04) 0px 2px 12px",
                }}
              >
                <h3
                  style={{
                    fontFamily: "Georgia, serif",
                    fontSize: "18px",
                    fontWeight: 500,
                    marginBottom: "4px",
                  }}
                >
                  Sources
                </h3>
                <p
                  style={{
                    fontFamily: "system-ui, sans-serif",
                    fontSize: "12px",
                    color: "var(--text-tertiary)",
                    marginBottom: "8px",
                  }}
                >
                  {report.num_sources} papers cited
                </p>
                {report.sources.map((s) => (
                  <SourceCard key={s.paper_id} source={s} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div
          style={{
            marginTop: "60px",
            paddingTop: "24px",
            borderTop: "1px solid var(--border-cream)",
            display: "flex",
            justifyContent: "flex-end",
          }}
        >
          <button
            onClick={handleClear}
            disabled={clearing}
            style={{
              fontFamily: "system-ui, sans-serif",
              fontSize: "13px",
              padding: "6px 14px",
              borderRadius: "6px",
              background: "var(--warm-sand)",
              color: "var(--text-tertiary)",
              border: "none",
              cursor: clearing ? "not-allowed" : "pointer",
              boxShadow: "0px 0px 0px 1px var(--ring-warm)",
            }}
          >
            {clearing ? "Clearing..." : "Clear vector store"}
          </button>
        </div>
      </div>
    </div>
  );
}