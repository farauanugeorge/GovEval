const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AnalysisResponse {
  job_id: string;
  slug: string;
  status: string;
}

export interface StatusResponse {
  status: string;
  progress_step: string | null;
  slug: string | null;
}

export interface EvidenceItem {
  claim: string;
  doi: string | null;
  title: string;
}

export interface VerdictResponse {
  slug: string;
  policy_text: string;
  verdict: "smart" | "mixed" | "poor";
  confidence: number;
  studies_used: number;
  summary: string;
  evidence_for: EvidenceItem[];
  evidence_against: EvidenceItem[];
  created_at: string;
}

export interface VerdictListItem {
  slug: string;
  verdict: string;
  confidence: number;
  studies_used: number;
  summary: string;
  created_at: string;
}

export interface VerdictListResponse {
  items: VerdictListItem[];
  total: number;
  page: number;
  page_size: number;
}

export async function submitAnalysis(
  inputType: string,
  content: string
): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE}/api/analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input_type: inputType, content }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Submission failed" }));
    throw new Error(err.detail || "Submission failed");
  }
  return res.json();
}

export async function getAnalysisStatus(
  jobId: string
): Promise<StatusResponse> {
  const res = await fetch(`${API_BASE}/api/analysis/${jobId}/status`);
  if (!res.ok) throw new Error("Failed to fetch status");
  return res.json();
}

export async function getVerdict(slug: string): Promise<VerdictResponse> {
  const res = await fetch(`${API_BASE}/api/verdict/${slug}`);
  if (!res.ok) throw new Error("Failed to fetch verdict");
  return res.json();
}

export async function getVerdicts(
  page = 1,
  pageSize = 20
): Promise<VerdictListResponse> {
  const res = await fetch(
    `${API_BASE}/api/verdicts?page=${page}&page_size=${pageSize}`
  );
  if (!res.ok) throw new Error("Failed to fetch verdicts");
  return res.json();
}
