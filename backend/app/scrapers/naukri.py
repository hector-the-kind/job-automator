import json
from datetime import datetime
from app.scrapers.base import BaseScraper


class NaukriScraper(BaseScraper):
    """Scraper for Naukri.com India."""
    
    portal_name = "naukri"
    base_url = "https://www.naukri.com"
    api_url = "https://www.naukri.com/jobapi/v3/search"
    
    async def search(self, query: str, location: str = "Hyderabad", page: int = 1) -> list[dict]:
        """Search Naukri jobs using internal API."""
        context = await self._get_browser()
        page_obj = await context.new_page()
        
        try:
            # First visit the homepage to get cookies
            await page_obj.goto(self.base_url, wait_until="networkidle", timeout=30000)
            await self._random_delay()
            
            # Use the search URL pattern
            search_url = f"{self.base_url}/{query.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}"
            if page > 1:
                search_url += f"-{page}"
            
            await page_obj.goto(search_url, wait_until="networkidle", timeout=30000)
            await self._random_delay()
            
            # Extract job cards
            jobs = await page_obj.evaluate("""
                () => {
                    const cards = document.querySelectorAll('.srp-grid-card');
                    return Array.from(cards).map(card => {
                        const titleEl = card.querySelector('.title');
                        const companyEl = card.querySelector('.companyName');
                        const locationEl = card.querySelector('.location');
                        const salaryEl = card.querySelector('.salary');
                        const linkEl = card.querySelector('a.title');
                        const expEl = card.querySelector('.experience');
                        
                        const url = linkEl?.href || '';
                        const jobId = url.match(/job\\/(\d+)/)?.[1] || '';
                        
                        return {
                            title: titleEl?.textContent?.trim() || '',
                            company: companyEl?.textContent?.trim() || '',
                            location: locationEl?.textContent?.trim() || '',
                            salary: salaryEl?.textContent?.trim() || '',
                            experience: expEl?.textContent?.trim() || '',
                            url: url,
                            portal_job_id: jobId,
                        };
                    }).filter(job => job.title && job.url);
                }
            """)
            
            # Parse and enrich jobs
            for job in jobs:
                job["portal"] = self.portal_name
                job["is_remote"] = "remote" in (job.get("location", "").lower())
                job["is_hybrid"] = "hybrid" in (job.get("location", "").lower())
                
                # Parse salary
                salary_min, salary_max = self.parse_salary(job.pop("salary", ""))
                job["salary_min"] = salary_min
                job["salary_max"] = salary_max
                
                # Parse experience
                job["experience_text"] = job.pop("experience", "")
            
            return jobs
            
        except Exception as e:
            print(f"[Naukri] Search error: {e}")
            return []
        finally:
            await page_obj.close()
    
    async def get_job_details(self, job_url: str) -> dict | None:
        """Get detailed job information from Naukri job page."""
        context = await self._get_browser()
        page_obj = await context.new_page()
        
        try:
            await page_obj.goto(job_url, wait_until="networkidle", timeout=30000)
            await self._random_delay()
            
            details = await page_obj.evaluate("""
                () => {
                    const descEl = document.querySelector('.job-description');
                    const skillsEl = document.querySelectorAll('.skill');
                    
                    const skills = Array.from(skillsEl).map(el => 
                        el.textContent?.trim()
                    ).filter(Boolean);
                    
                    return {
                        description: descEl?.textContent?.trim() || '',
                        skills: skills,
                    };
                }
            """)
            
            return details
            
        except Exception as e:
            print(f"[Naukri] Details error: {e}")
            return None
        finally:
            await page_obj.close()
