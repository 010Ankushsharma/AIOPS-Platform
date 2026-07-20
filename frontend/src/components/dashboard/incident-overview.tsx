"use client";

const mockIncidents = [
  { id: "INC-000042", title: "Payment service high latency", severity: "P1", status: "investigating", service: "payment-service", age: "12m" },
  { id: "INC-000041", title: "Database connection pool exhaustion", severity: "P0", status: "identified", service: "order-service", age: "45m" },
  { id: "INC-000040", title: "Increased error rate on auth endpoint", severity: "P2", status: "open", service: "auth-service", age: "2h" },
];

const severityColors: Record<string, string> = {
  P0: "bg-red-500 text-white",
  P1: "bg-orange-500 text-white",
  P2: "bg-yellow-500 text-black",
  P3: "bg-blue-500 text-white",
};

export function IncidentOverview() {
  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900/50">
      <div className="p-4 border-b border-gray-800 flex justify-between items-center">
        <h2 className="font-semibold">Active Incidents</h2>
        <button className="text-xs text-red-400 hover:text-red-300">View All →</button>
      </div>
      <div className="divide-y divide-gray-800">
        {mockIncidents.map((incident) => (
          <div key={incident.id} className="p-4 hover:bg-gray-800/50 transition-colors cursor-pointer">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${severityColors[incident.severity]}`}>
                  {incident.severity}
                </span>
                <div>
                  <p className="text-sm font-medium">{incident.title}</p>
                  <p className="text-xs text-gray-500">{incident.id} · {incident.service} · {incident.age}</p>
                </div>
              </div>
              <span className="text-xs px-2 py-1 rounded-full bg-gray-800 text-gray-300">
                {incident.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
