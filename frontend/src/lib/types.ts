export interface Job {
  id: number;
  portal: string;
  portal_job_id: string;
  title: string;
  company: string | null;
  location: string | null;
  is_remote: boolean;
  is_hybrid: boolean;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string;
  job_type: string | null;
  description: string | null;
  requirements: string[];
  skills_required: string[];
  url: string;
  company_url: string | null;
  posted_at: string | null;
  scraped_at: string;
  is_active: boolean;
  match_score: number | null;
  location_match: boolean;
}

export interface Application {
  id: number;
  user_id: number;
  job_id: number;
  status: ApplicationStatus;
  match_score: number;
  auto_applied: boolean;
  applied_at: string | null;
  portal_application_id: string | null;
  cover_letter_used: string | null;
  custom_answers: Record<string, unknown>;
  interview_date: string | null;
  outcome: string | null;
  offer_salary: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  job?: Job;
}

export type ApplicationStatus =
  | "discovered"
  | "to_apply"
  | "applied"
  | "screening"
  | "interview"
  | "completed";

export interface DashboardStats {
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
}

export interface UserProfile {
  id: number;
  full_name: string | null;
  email: string | null;
  phone: string | null;
  telegram_chat_id: string | null;
  skills: string[];
  experience_years: number;
  education: Record<string, unknown>[];
  job_titles: string[];
  preferred_locations: string[];
  remote_preference: string;
  desired_salary_min: number | null;
  desired_salary_max: number | null;
  auto_apply_threshold: number;
  search_keywords: string[];
  active_portals: string[];
  created_at: string;
  updated_at: string;
}
