const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export const api = {
  // Dashboard
  getDashboardStats: () => fetchApi<{
    total_jobs_scraped: number;
    total_applications: number;
    discovered: number;
    to_apply: number;
    applied: number;
    screening: number;
    interview: number;
    completed: number;
    offer_count: number;
    rejected_count: number;
    response_rate: number;
  }>("/dashboard/stats"),

  // Jobs
  getJobs: (params?: { portal?: string; min_score?: number; page?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.portal) searchParams.set("portal", params.portal);
    if (params?.min_score) searchParams.set("min_score", params.min_score.toString());
    if (params?.page) searchParams.set("page", params.page.toString());
    return fetchApi<{ jobs: any[]; total: number }>(`/jobs?${searchParams}`);
  },

  getJob: (id: number) => fetchApi<any>(`/jobs/${id}`),

  // Applications
  getApplications: (params?: { status?: string; page?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.page) searchParams.set("page", params.page.toString());
    return fetchApi<{ applications: any[]; total: number }>(`/applications?${searchParams}`);
  },

  approveApplication: (id: number) =>
    fetchApi<any>(`/applications/${id}/approve`, { method: "POST" }),

  declineApplication: (id: number) =>
    fetchApi<any>(`/applications/${id}/decline`, { method: "POST" }),

  updateApplication: (id: number, data: { status?: string; notes?: string }) =>
    fetchApi<any>(`/applications/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Profile
  getProfile: () => fetchApi<any>("/profile"),

  updateProfile: (data: Record<string, unknown>) =>
    fetchApi<any>("/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};
