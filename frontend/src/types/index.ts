export interface Incident {
  id: string;
  title: string;
  description: string | null;
  severity: "P0" | "P1" | "P2" | "P3";
  status: "open" | "investigating" | "identified" | "mitigated" | "resolved" | "closed";
  service_id: string | null;
  root_cause: string | null;
  root_cause_confidence: number | null;
  remediation_plan: Record<string, any>;
  timeline: Array<Record<string, any>>;
  tags: string[];
  detected_at: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface RCAReport {
  id: string;
  incident_id: string;
  root_cause: string;
  confidence: number;
  evidence: Array<{ type: string; detail: string }>;
  affected_services: string[];
  remediation_steps: Array<{ step: number; action: string; risk: string }>;
  created_at: string;
}

export interface Analytics {
  period_start: string;
  period_end: string;
  total_incidents: number;
  mttr_minutes: number;
  mttd_minutes: number;
  incidents_by_severity: Record<string, number>;
  incidents_by_service: Record<string, number>;
  ai_accuracy: number;
  auto_resolved_count: number;
}

export interface Service {
  id: string;
  name: string;
  description: string;
  tier: number;
  team_id: string;
  repository_url: string;
}
