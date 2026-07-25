"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { UserProfile } from "@/lib/types";

const PORTALS = ["linkedin", "naukri", "wellfound", "cutshort", "iimjobs", "hirect", "foundit", "indeed"];

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [telegramChatId, setTelegramChatId] = useState("");
  const [skills, setSkills] = useState("");
  const [experienceYears, setExperienceYears] = useState(0);
  const [jobTitles, setJobTitles] = useState("");
  const [preferredLocations, setPreferredLocations] = useState("");
  const [remotePreference, setRemotePreference] = useState("remote");
  const [salaryMin, setSalaryMin] = useState("");
  const [salaryMax, setSalaryMax] = useState("");
  const [autoApplyThreshold, setAutoApplyThreshold] = useState(90);
  const [searchKeywords, setSearchKeywords] = useState("");
  const [activePortals, setActivePortals] = useState<string[]>(PORTALS);
  const [resumeText, setResumeText] = useState("");

  useEffect(() => {
    api.getProfile().then((p) => {
      setProfile(p);
      setFullName(p.full_name || "");
      setEmail(p.email || "");
      setPhone(p.phone || "");
      setTelegramChatId(p.telegram_chat_id || "");
      setSkills((p.skills || []).join(", "));
      setExperienceYears(p.experience_years || 0);
      setJobTitles((p.job_titles || []).join(", "));
      setPreferredLocations((p.preferred_locations || []).join(", "));
      setRemotePreference(p.remote_preference || "remote");
      setSalaryMin(p.desired_salary_min?.toString() || "");
      setSalaryMax(p.desired_salary_max?.toString() || "");
      setAutoApplyThreshold(p.auto_apply_threshold ?? 90);
      setSearchKeywords((p.search_keywords || []).join(", "));
      setActivePortals(p.active_portals || PORTALS);
      setResumeText(p.resume_text || "");
      setLoading(false);
    }).catch(() => {
      setError("Failed to load profile");
      setLoading(false);
    });
  }, []);

  function parseList(val: string): string[] {
    return val.split(",").map((s) => s.trim()).filter(Boolean);
  }

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    try {
      await api.updateProfile({
        full_name: fullName || null,
        email: email || null,
        phone: phone || null,
        telegram_chat_id: telegramChatId || null,
        skills: parseList(skills),
        experience_years: experienceYears,
        job_titles: parseList(jobTitles),
        preferred_locations: parseList(preferredLocations),
        remote_preference: remotePreference,
        desired_salary_min: salaryMin ? parseInt(salaryMin) : null,
        desired_salary_max: salaryMax ? parseInt(salaryMax) : null,
        auto_apply_threshold: autoApplyThreshold,
        search_keywords: parseList(searchKeywords),
        active_portals: activePortals,
        resume_text: resumeText || null,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      setError("Failed to save profile");
    } finally {
      setSaving(false);
    }
  }

  function togglePortal(portal: string) {
    setActivePortals((prev) =>
      prev.includes(portal) ? prev.filter((p) => p !== portal) : [...prev, portal]
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Profile & Settings</h1>
            <p className="text-sm text-gray-500">Configure your job search preferences</p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Personal Info */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Full Name" value={fullName} onChange={setFullName} placeholder="John Doe" />
            <Field label="Email" value={email} onChange={setEmail} placeholder="john@example.com" />
            <Field label="Phone" value={phone} onChange={setPhone} placeholder="+91 ..." />
            <Field label="Telegram Chat ID" value={telegramChatId} onChange={setTelegramChatId} placeholder="123456789" />
          </div>
        </section>

        {/* Professional Info */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Professional Profile</h2>
          <div className="space-y-4">
            <Field label="Skills (comma-separated)" value={skills} onChange={setSkills} placeholder="product strategy, analytics, SQL, Figma" />
            <Field label="Target Job Titles (comma-separated)" value={jobTitles} onChange={setJobTitles} placeholder="Product Manager, Builder PM" />
            <div className="grid grid-cols-2 gap-4">
              <Field label="Experience (years)" value={experienceYears.toString()} onChange={(v) => setExperienceYears(parseInt(v) || 0)} type="number" />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Remote Preference</label>
                <select
                  value={remotePreference}
                  onChange={(e) => setRemotePreference(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="remote">Remote Only</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">On-site</option>
                  <option value="any">Any</option>
                </select>
              </div>
            </div>
            <Field label="Preferred Locations (comma-separated)" value={preferredLocations} onChange={setPreferredLocations} placeholder="Hyderabad, Bangalore" />
            <div className="grid grid-cols-2 gap-4">
              <Field label="Min Salary (₹)" value={salaryMin} onChange={setSalaryMin} type="number" placeholder="1500000" />
              <Field label="Max Salary (₹)" value={salaryMax} onChange={setSalaryMax} type="number" placeholder="3000000" />
            </div>
          </div>
        </section>

        {/* Search Settings */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Settings</h2>
          <div className="space-y-4">
            <Field label="Search Keywords (comma-separated)" value={searchKeywords} onChange={setSearchKeywords} placeholder="product manager, builder PM" />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Auto-Apply Threshold: {autoApplyThreshold}%
              </label>
              <input
                type="range"
                min="50"
                max="100"
                value={autoApplyThreshold}
                onChange={(e) => setAutoApplyThreshold(parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-gray-500 mt-1">Jobs scoring above this will be auto-applied</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Active Portals</label>
              <div className="flex flex-wrap gap-2">
                {PORTALS.map((portal) => (
                  <button
                    key={portal}
                    onClick={() => togglePortal(portal)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                      activePortals.includes(portal)
                        ? "bg-blue-600 text-white border-blue-600"
                        : "bg-white text-gray-600 border-gray-300 hover:border-gray-400"
                    }`}
                  >
                    {portal}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Resume */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Resume</h2>
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            rows={8}
            placeholder="Paste your resume text here for better job matching..."
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </section>

        {/* Save */}
        <div className="flex items-center gap-4">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Profile"}
          </button>
          {saved && <span className="text-green-600 text-sm font-medium">Saved!</span>}
        </div>
      </main>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
      />
    </div>
  );
}
