"use client";

import { Search, Send, Phone, CheckCircle, FileSearch, Briefcase } from "lucide-react";
import type { DashboardStats } from "@/lib/types";

interface StatsCardsProps {
  stats: DashboardStats;
}

const cards = [
  { label: "Jobs Scraped", key: "total_jobs_scraped" as const, Icon: Search, color: "text-blue-600", bg: "bg-blue-50" },
  { label: "To Apply", key: "to_apply" as const, Icon: FileSearch, color: "text-amber-600", bg: "bg-amber-50" },
  { label: "Applied", key: "applied" as const, Icon: Send, color: "text-green-600", bg: "bg-green-50" },
  { label: "Screening", key: "screening" as const, Icon: Phone, color: "text-purple-600", bg: "bg-purple-50" },
  { label: "Interviews", key: "interview" as const, Icon: Briefcase, color: "text-indigo-600", bg: "bg-indigo-50" },
  { label: "Completed", key: "completed" as const, Icon: CheckCircle, color: "text-emerald-600", bg: "bg-emerald-50" },
];

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`${card.bg} rounded-lg p-4 border border-gray-100`}
        >
          <div className="flex items-center gap-2 mb-1">
            <card.Icon className={`w-4 h-4 ${card.color}`} />
            <p className="text-sm font-medium text-gray-600">{card.label}</p>
          </div>
          <p className={`text-2xl font-bold ${card.color} mt-1`}>
            {stats[card.key]}
          </p>
        </div>
      ))}

      {/* Response Rate */}
      <div className="col-span-2 md:col-span-3 lg:col-span-6 bg-white rounded-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Response Rate</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {stats.response_rate}%
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">
              {stats.total_applications} total applications
            </p>
          </div>
        </div>
        <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(stats.response_rate, 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
