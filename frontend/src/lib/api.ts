import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("aiops_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API functions
export const incidentsApi = {
  list: (params?: { status?: string; severity?: string }) => 
    api.get("/incidents", { params }),
  get: (id: string) => api.get(`/incidents/${id}`),
  create: (data: any) => api.post("/incidents", data),
  analyze: (incidentId: string) => 
    api.post("/incidents/analyze", { incident_id: incidentId }),
  remediate: (incidentId: string) => 
    api.post(`/incidents/${incidentId}/remediate`),
};

export const analyticsApi = {
  get: (days?: number) => api.get("/analytics", { params: { days } }),
  trends: (days?: number) => api.get("/analytics/trends", { params: { days } }),
};

export const githubApi = {
  createPR: (data: any) => api.post("/github/pr", data),
};

export const authApi = {
  login: (email: string, password: string) => 
    api.post("/auth/login", { email, password }),
};
