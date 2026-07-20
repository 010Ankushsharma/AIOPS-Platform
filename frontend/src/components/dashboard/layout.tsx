"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AlertTriangle, BarChart3, Bot, GitPullRequest,
  LayoutDashboard, Settings, Shield, Activity
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Incidents", href: "/incidents", icon: AlertTriangle },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "AI Copilot", href: "/copilot", icon: Bot },
  { name: "Deployments", href: "/deployments", icon: GitPullRequest },
  { name: "Services", href: "/services", icon: Activity },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-red-500" />
            <span className="font-bold text-lg">AIOps</span>
          </div>
          <p className="text-xs text-gray-500 mt-1">AI Operations Engineer</p>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-red-500/10 text-red-400 border border-red-500/20"
                    : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-gray-700 flex items-center justify-center text-xs">
              AS
            </div>
            <div>
              <p className="text-sm font-medium">Ankush Sharma</p>
              <p className="text-xs text-gray-500">SRE</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
