"use client";

import type { Application, ApplicationStatus } from "@/lib/types";

interface JobCardProps {
  application: Application;
  onApprove: () => void;
  onDecline: () => void;
  onStatusChange: (appId: number, newStatus: ApplicationStatus) => void;
  loading: boolean;
}

const portalColors: Record<string, string> = {
  linkedin: "bg-blue-100 text-blue-700",
  naukri: "bg-orange-100 text-orange-700",
  wellfound: "bg-purple-100 text-purple-700",
  cutshort: "bg-green-100 text-green-700",
  iimjobs: "bg-indigo-100 text-indigo-700",
  hirect: "bg-red-100 text-red-700",
  foundit: "bg-cyan-100 text-cyan-700",
  indeed: "bg-blue-100 text-blue-700",
};

const nextStatus: Partial<Record<ApplicationStatus, { status: ApplicationStatus; label: string }>> = {
  to_apply: { status: "applied", label: "Mark Applied" },
  applied: { status: "screening", label: "Mark Screening" },
  screening: { status: "interview", label: "Mark Interview" },
  interview: { status: "completed", label: "Mark Completed" },
};

function getScoreColor(score: number): string {
  if (score >= 90) return "text-green-600 bg-green-50";
  if (score >= 75) return "text-blue-600 bg-blue-50";
  if (score >= 60) return "text-amber-600 bg-amber-50";
  return "text-gray-600 bg-gray-50";
}

export function JobCard({ application, onApprove, onDecline, onStatusChange, loading }: JobCardProps) {
  const job = application.job;

  if (!job) return null;

  const scoreColor = getScoreColor(application.match_score);
  const portalColor = portalColors[job.portal] || "bg-gray-100 text-gray-700";
  const next = nextStatus[application.status];

  return (
    <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
      {/* Portal Badge */}
      <div className="flex items-center justify-between mb-2">
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${portalColor}`}>
          {job.portal}
        </span>
        {application.auto_applied && (
          <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">
            Auto
          </span>
        )}
      </div>

      {/* Job Title */}
      <h4 className="font-medium text-gray-900 text-sm leading-tight mb-1">
        {job.title}
      </h4>

      {/* Company */}
      <p className="text-gray-600 text-sm mb-2">{job.company}</p>

      {/* Location */}
      <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
        <span>{job.is_remote ? "🌍 Remote" : "📍 " + (job.location || "Not specified")}</span>
      </div>

      {/* Salary */}
      {(job.salary_min || job.salary_max) && (
        <p className="text-xs text-gray-500 mb-2">
          ₹{job.salary_min?.toLocaleString() || "?"} - ₹{job.salary_max?.toLocaleString() || "?"}
        </p>
      )}

      {/* Match Score */}
      <div className={`inline-flex items-center px-2 py-1 rounded ${scoreColor}`}>
        <span className="text-xs font-semibold">{application.match_score}%</span>
        <span className="text-xs ml-1">match</span>
      </div>

      {/* Actions */}
      <div className="mt-3 flex gap-2">
        {application.status === "discovered" && (
          <>
            <button
              onClick={onApprove}
              disabled={loading}
              className="flex-1 px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? "..." : "Apply"}
            </button>
            <button
              onClick={onDecline}
              disabled={loading}
              className="flex-1 px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-medium rounded hover:bg-gray-300 disabled:opacity-50"
            >
              Skip
            </button>
          </>
        )}
        {next && (
          <button
            onClick={() => onStatusChange(application.id, next.status)}
            disabled={loading}
            className="flex-1 px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "..." : next.label}
          </button>
        )}
        {application.status !== "discovered" && (
          <button
            onClick={onDecline}
            disabled={loading}
            className="px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-medium rounded hover:bg-gray-300 disabled:opacity-50"
          >
            ✕
          </button>
        )}
        <a
          href={`/jobs/${job.id}`}
          className="px-3 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded hover:bg-gray-200 text-center"
        >
          Details
        </a>
        <a
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          className="px-3 py-1.5 bg-blue-50 text-blue-700 text-xs font-medium rounded hover:bg-blue-100 text-center"
        >
          JD
        </a>
      </div>
    </div>
  );
}
