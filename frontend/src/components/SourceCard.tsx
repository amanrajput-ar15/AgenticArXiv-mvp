interface Source {
  paper_id: string;
  title: string;
  authors: string[];
  published: string;
}

export function SourceCard({ source }: { source: Source }) {
  const year    = source.published?.slice(0, 4) ?? "";
  const authors = (source.authors ?? []).slice(0, 2).join(", ");
  const url     = `https://arxiv.org/abs/${source.paper_id}`;

  return (
    <div
      style={{
        padding: "14px 0",
        borderTop: "1px solid var(--border-cream)",
      }}
    >
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          fontFamily: "Georgia, serif",
          fontSize: "15px",
          fontWeight: 500,
          color: "var(--text-primary)",
          textDecoration: "none",
          display: "block",
          marginBottom: "4px",
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {source.title}
      </a>
      <p
        style={{
          fontFamily: "system-ui, sans-serif",
          fontSize: "13px",
          color: "var(--text-tertiary)",
          margin: 0,
        }}
      >
        {authors} {year && `· ${year}`} ·{" "}
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "var(--coral)", textDecoration: "none" }}
        >
          arXiv →
        </a>
      </p>
    </div>
  );
}
