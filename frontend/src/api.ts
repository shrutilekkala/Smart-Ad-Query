export interface AdMetrics {
  id: number;
  campaign_name: string;
  platform: string;
  ad_copy: string;
  target_audience: string;
  date: string;
  impressions: number;
  clicks: number;
  spend: number;
  conversions: number;
  revenue: number;
  ctr: number;
  cpc: number;
  roas: number;
}

export interface SearchResult {
  ad: AdMetrics;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
}

export interface RagResponse {
  question: string;
  answer: string;
  sources: SearchResult[];
  generated_by: "llm" | "extractive";
}

export interface CampaignSummary {
  campaign_name: string;
  platform: string;
  impressions: number;
  clicks: number;
  spend: number;
  revenue: number;
  ctr: number;
  roas: number;
}

export interface AnalyticsSummary {
  total_spend: number;
  total_revenue: number;
  total_impressions: number;
  total_clicks: number;
  overall_ctr: number;
  overall_roas: number;
  campaigns: CampaignSummary[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  search: (q: string, topK = 5) =>
    request<SearchResponse>(`/api/search?q=${encodeURIComponent(q)}&top_k=${topK}`),

  ragQuery: (question: string, topK = 5) =>
    request<RagResponse>("/api/query", {
      method: "POST",
      body: JSON.stringify({ question, top_k: topK }),
    }),

  analyticsSummary: () => request<AnalyticsSummary>("/api/analytics/summary"),
};
