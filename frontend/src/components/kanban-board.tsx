"use client";

import { useState } from "react";
import { JobCard } from "./job-card";
import { api } from "@/lib/api";
import { useToast } from "./toast";
import type { Application, ApplicationStatus } from "@/lib/types";

interface KanbanBoardProps {
  applications: Application[];
  onUpdate: () => void;
}

const columns: { status: ApplicationStatus; label: string; color: string }[] = [
  { status: "discovered", label: "Discovered", color: "bg-gray-100" },
  { status: "to_apply", label: "To Apply", color: "bg-amber-50" },
  { status: "applied", label: "Applied", color: "bg-green-50" },
  { status: "screening", label: "Screening", color: "bg-purple-50" },
  { status: "interview", label: "Interview", color: "bg-indigo-50" },
  { status: "completed", label: "Completed", color: "bg-emerald-50" },
];

export function KanbanBoard({ applications, onUpdate }: KanbanBoardProps) {
  const [loading, setLoading] = useState<number | null>(null);
  const { addToast } = useToast();

  const getColumnApps = (status: ApplicationStatus) =>
    applications.filter((app) => app.status === status);

  const handleApprove = async (appId: number) => {
    try {
      setLoading(appId);
      await api.approveApplication(appId);
      onUpdate();
    } catch (err) {
      addToast("Failed to approve application");
    } finally {
      setLoading(null);
    }
  };

  const handleDecline = async (appId: number) => {
    try {
      setLoading(appId);
      await api.declineApplication(appId);
      onUpdate();
    } catch (err) {
      addToast("Failed to decline application");
    } finally {
      setLoading(null);
    }
  };

  const handleStatusChange = async (appId: number, newStatus: ApplicationStatus) => {
    try {
      setLoading(appId);
      await api.updateApplication(appId, { status: newStatus });
      onUpdate();
    } catch (err) {
      addToast("Failed to update status");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map((col) => {
        const colApps = getColumnApps(col.status);
        return (
          <div
            key={col.status}
            className={`flex-shrink-0 w-72 ${col.color} rounded-lg p-3`}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-900 text-sm">{col.label}</h3>
              <span className="bg-white px-2 py-0.5 rounded-full text-xs font-medium text-gray-600">
                {colApps.length}
              </span>
            </div>
            <div className="space-y-3">
              {colApps.map((app) => (
                <JobCard
                  key={app.id}
                  application={app}
                  onApprove={() => handleApprove(app.id)}
                  onDecline={() => handleDecline(app.id)}
                  onStatusChange={handleStatusChange}
                  loading={loading === app.id}
                />
              ))}
              {colApps.length === 0 && (
                <p className="text-center text-gray-400 text-sm py-8">
                  No applications
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
