import type { JobStatus } from "@/types/api";

const API = process.env.NEXT_PUBLIC_API_URL!;

export async function uploadPDF(file: File): Promise<{ job_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function conductResearch(
  query: string,
  k = 15
): Promise<{ job_id: string }> {
  const res = await fetch(`${API}/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, retrieval_k: k }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${API}/status/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export async function getHealth(): Promise<{ status: string; total_chunks: number }> {
  const res = await fetch(`${API}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function clearVectorStore(): Promise<{ status: string }> {
  const res = await fetch(`${API}/vectorstore`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to clear vector store");
  return res.json();
}

export function pollUntilDone(
  jobId: string,
  onProgress?: (job: JobStatus) => void,
  intervalMs = 2000
): Promise<JobStatus> {
  return new Promise((resolve, reject) => {
    const iv = setInterval(async () => {
      try {
        const job = await getStatus(jobId);
        onProgress?.(job);
        if (job.status === "DONE") {
          clearInterval(iv);
          resolve(job);
        }
        if (job.status === "FAILED") {
          clearInterval(iv);
          reject(new Error(job.error ?? "Job failed"));
        }
      } catch (e) {
        clearInterval(iv);
        reject(e);
      }
    }, intervalMs);
  });
}
