// types/api.ts

export interface JobResponse {
  job_id: string;
  status: "PENDING";
}

export interface JobStatus {
  status: "PENDING" | "PROCESSING" | "DONE" | "FAILED";
  type: "ingest" | "research";
  created_at: string;
  started_at?: string;
  completed_at?: string;
  agents_completed?: string[];
  result?: IngestResult | ResearchReport;
  error?: string;
}

export interface IngestResult {
  pages_processed: number;
  chunks_created: number;
}

export interface ResearchReport {
  query: string;
  literature_review: string;
  methods_analysis: string;
  results_analysis: string;
  critique: string;
  synthesis: string;
  sources: Source[];
  num_sources: number;
}

export interface Source {
  paper_id: string;
  title: string;
  authors: string[];
  published: string;
}

export interface HealthStatus {
  status: "ok";
  total_chunks: number;
}
