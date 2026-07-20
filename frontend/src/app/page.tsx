import { DashboardLayout } from "@/components/dashboard/layout";
import { IncidentOverview } from "@/components/dashboard/incident-overview";
import { MetricsPanel } from "@/components/dashboard/metrics-panel";
import { AlertTimeline } from "@/components/dashboard/alert-timeline";
import { ServiceHealth } from "@/components/dashboard/service-health";

export default function HomePage() {
  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Operations Dashboard</h1>
            <p className="text-gray-400 text-sm">
              Real-time infrastructure health and incident overview
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-900 text-green-300">
              All Systems Operational
            </span>
          </div>
        </header>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <KPICard title="Active Incidents" value="3" trend="-2" color="red" />
          <KPICard title="MTTR" value="23.5 min" trend="-12%" color="green" />
          <KPICard title="AI Accuracy" value="89%" trend="+3%" color="blue" />
          <KPICard title="Auto-Resolved" value="14" trend="+5" color="purple" />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <IncidentOverview />
          </div>
          <div>
            <ServiceHealth />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MetricsPanel />
          <AlertTimeline />
        </div>
      </div>
    </DashboardLayout>
  );
}

function KPICard({ title, value, trend, color }: { 
  title: string; value: string; trend: string; color: string 
}) {
  const colors: Record<string, string> = {
    red: "border-red-500/30 bg-red-950/20",
    green: "border-green-500/30 bg-green-950/20",
    blue: "border-blue-500/30 bg-blue-950/20",
    purple: "border-purple-500/30 bg-purple-950/20",
  };
  
  return (
    <div className={`rounded-lg border p-4 ${colors[color]}`}>
      <p className="text-sm text-gray-400">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{trend} vs last week</p>
    </div>
  );
}
