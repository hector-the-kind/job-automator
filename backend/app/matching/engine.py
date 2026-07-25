import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import get_settings

settings = get_settings()


class MatchEngine:
    def __init__(self, profile: dict, resume_text: str):
        self.profile = profile
        self.user_skills = set(s.lower() for s in (profile.get("skills") or []))
        self.user_titles = [t.lower() for t in (profile.get("job_titles") or [])]
        self.resume_text = resume_text or ""
        
        # Build TF-IDF for resume
        if self.resume_text:
            self.vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=5000,
                ngram_range=(1, 2)
            )
            self.resume_tfidf = self.vectorizer.fit_transform([self.resume_text])
        else:
            self.vectorizer = None
            self.resume_tfidf = None
    
    def score(self, job: dict) -> tuple[float, bool]:
        """
        Calculate match score for a job.
        Returns (score: 0-100, location_match: bool)
        """
        scores = {}
        
        # 1. TF-IDF similarity (weight: 0.4)
        scores["tfidf"] = self._tfidf_score(job.get("description", ""))
        
        # 2. Skill overlap (weight: 0.4)
        scores["skills"] = self._skill_overlap(job.get("skills_required", []))
        
        # 3. Title similarity (weight: 0.15)
        scores["title"] = self._title_similarity(job.get("title", ""))
        
        # 4. Experience match (weight: 0.05)
        scores["experience"] = self._experience_match(job)
        
        # Weighted sum
        total_score = (
            scores["tfidf"] * 0.4 +
            scores["skills"] * 0.4 +
            scores["title"] * 0.15 +
            scores["experience"] * 0.05
        ) * 100
        
        # Location match check
        location_match = self._check_location_match(job)
        
        # Penalize if location doesn't match
        if not location_match:
            total_score *= 0.5
        
        return round(min(total_score, 100), 1), location_match
    
    def _tfidf_score(self, job_description: str) -> float:
        """Cosine similarity between resume and job description."""
        if not self.vectorizer or not self.resume_tfidf or not job_description:
            return 0.0
        
        try:
            job_tfidf = self.vectorizer.transform([job_description])
            similarity = cosine_similarity(self.resume_tfidf, job_tfidf)[0][0]
            return float(similarity)
        except Exception:
            return 0.0
    
    def _skill_overlap(self, required_skills: list[str]) -> float:
        """Ratio of required skills that user has."""
        if not required_skills:
            return 0.5  # Neutral if no skills listed
        
        required_set = set(s.lower().strip() for s in required_skills)
        
        # Exact match
        exact_matches = len(required_set & self.user_skills)
        
        # Partial/fuzzy match
        partial_matches = 0
        for req_skill in required_set:
            if req_skill not in self.user_skills:
                # Check for partial match
                for user_skill in self.user_skills:
                    if req_skill in user_skill or user_skill in req_skill:
                        partial_matches += 0.5
                        break
                    elif SequenceMatcher(None, req_skill, user_skill).ratio() > 0.7:
                        partial_matches += 0.3
                        break
        
        total_matches = exact_matches + partial_matches
        return min(total_matches / len(required_set), 1.0) if required_set else 0.5
    
    def _title_similarity(self, job_title: str) -> float:
        """Fuzzy match between job title and user's target titles."""
        if not job_title or not self.user_titles:
            return 0.0
        
        job_title_lower = job_title.lower()
        
        best_match = 0.0
        for user_title in self.user_titles:
            ratio = SequenceMatcher(None, job_title_lower, user_title).ratio()
            best_match = max(best_match, ratio)
            
            # Check if key terms overlap
            job_terms = set(re.findall(r'\w+', job_title_lower))
            user_terms = set(re.findall(r'\w+', user_title))
            term_overlap = len(job_terms & user_terms) / max(len(job_terms | user_terms), 1)
            best_match = max(best_match, term_overlap)
        
        return best_match
    
    def _experience_match(self, job: dict) -> float:
        """Check if user's experience matches job requirements."""
        user_years = self.profile.get("experience_years", 0)
        
        # Try to extract experience from job requirements
        desc = job.get("description", "") or ""
        requirements = job.get("requirements", []) or []
        
        # Look for patterns like "3+ years", "5-7 years"
        exp_patterns = re.findall(r'(\d+)\+?\s*(?:to|-)?\s*(\d+)?\s*years?(?:\s*of)?\s*(?:experience)?', desc)
        
        if not exp_patterns:
            return 0.5  # Neutral if no requirement found
        
        for min_exp, max_exp in exp_patterns:
            min_exp = int(min_exp)
            max_exp = int(max_exp) if max_exp else min_exp + 5
            
            if min_exp <= user_years <= max_exp:
                return 1.0
            elif user_years < min_exp:
                return max(0.3, 1.0 - (min_exp - user_years) * 0.1)
            else:
                return max(0.5, 1.0 - (user_years - max_exp) * 0.05)
        
        return 0.5
    
    def _check_location_match(self, job: dict) -> bool:
        """Check if job location matches user preferences."""
        job_location = (job.get("location") or "").lower()
        is_remote = job.get("is_remote", False)
        is_hybrid = job.get("is_hybrid", False)
        
        # Remote jobs - accept anywhere in India
        if is_remote:
            return True
        
        # Check if location contains India or Indian cities
        india_keywords = ["india", "hyderabad", "bangalore", "mumbai", "delhi", "pune", "chennai"]
        if any(city in job_location for city in india_keywords):
            # For in-person/hybrid - must be Hyderabad
            if not is_remote:
                return "hyderabad" in job_location
            return True
        
        # If no clear location info, assume match
        if not job_location:
            return True
        
        return False


def extract_skills_from_text(text: str) -> list[str]:
    """Extract skills from job description text."""
    # Common PM skills
    pm_skills = [
        "product management", "product strategy", "roadmap", "user research",
        "data analysis", "sql", "python", "analytics", "a/b testing",
        "agile", "scrum", "jira", "confluence", "figma", "user experience",
        "ux", "ui", "stakeholder management", "cross-functional",
        "metrics", "kpi", "okr", "gtm", "go-to-market", "pricing",
        "market research", "competitive analysis", "customer development",
        "wireframing", "prototyping", "user stories", "backlog",
        "sprint", "lean", "growth", "retention", "engagement",
        "monetization", "platform", "api", "technical", "engineering",
        "design thinking", "jobs to be done", "jtbd"
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in pm_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return found_skills
