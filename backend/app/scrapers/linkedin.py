import re
from datetime import datetime
from urllib.parse import urlencode
from app.scrapers.base import BaseScraper


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn Jobs India."""
    
    portal_name = "linkedin"
    base_url = "https://www.linkedin.com/jobs/search"
    
    async def search(self, query: str, location: str = "India", page: int = 1) -> list[dict]:
        """Search LinkedIn jobs."""
        context = await self._get_browser()
        page_obj = await context.new_page()
        
        try:
            params = {
                "keywords": query,
                "location": location,
                "f_TPR": "r604800",  # Past week
                "start": (page - 1) * 25,
                "sortBy": "DD",  # Sort by date
            }
            
            url = f"{self.base_url}?{urlencode(params)}"
            await page_obj.goto(url, wait_until="networkidle", timeout=30000)
            await self._random_delay()
            
            # Extract job cards
            jobs = await page_obj.evaluate("""
                () => {
                    const cards = document.querySelectorAll('.job-search-card');
                    return Array.from(cards).map(card => {
                        const titleEl = card.querySelector('.base-search-card__title');
                        const companyEl = card.querySelector('.base-search-card__subtitle a');
                        const locationEl = card.querySelector('.job-search-card__location');
                        const dateEl = card.querySelector('time');
                        const linkEl = card.querySelector('a.base-card__full-link');
                        
                        return {
                            title: titleEl?.textContent?.trim() || '',
                            company: companyEl?.textContent?.trim() || '',
                            location: locationEl?.textContent?.trim() || '',
                            url: linkEl?.href || '',
                            posted_at: dateEl?.getAttribute('datetime') || '',
                        };
                    }).filter(job => job.title && job.url);
                }
            """)
            
            # Enrich with portal info
            for job in jobs:
                job["portal"] = self.portal_name
                job["portal_job_id"] = self._extract_job_id(job["url"])
                job["is_remote"] = "remote" in (job.get("location", "").lower())
                job["is_hybrid"] = "hybrid" in (job.get("location", "").lower())
            
            return jobs
            
        except Exception as e:
            print(f"[LinkedIn] Search error: {e}")
            return []
        finally:
            await page_obj.close()
    
    async def get_job_details(self, job_url: str) -> dict | None:
        """Get detailed job information from LinkedIn job page."""
        context = await self._get_browser()
        page_obj = await context.new_page()
        
        try:
            await page_obj.goto(job_url, wait_until="networkidle", timeout=30000)
            await self._random_delay()
            
            details = await page_obj.evaluate("""
                () => {
                    const descEl = document.querySelector('.show-more-less-html__markup');
                    const criteriaEl = document.querySelectorAll('.job-criteria__item');
                    
                    const criteria = {};
                    criteriaEl.forEach(item => {
                        const header = item.querySelector('.job-criteria__subheader')?.textContent?.trim();
                        const value = item.querySelector('.job-criteria__text')?.textContent?.trim();
                        if (header && value) {
                            criteria[header.toLowerCase()] = value;
                        }
                    });
                    
                    return {
                        description: descEl?.textContent?.trim() || '',
                        employment_type: criteria['employment type'] || '',
                        seniority_level: criteria['seniority level'] || '',
                        industry: criteria['industry'] || '',
                    };
                }
            """)
            
            return details
            
        except Exception as e:
            print(f"[LinkedIn] Details error: {e}")
            return None
        finally:
            await page_obj.close()
    
    def _extract_job_id(self, url: str) -> str:
        """Extract job ID from LinkedIn URL."""
        match = re.search(r'/view/.*?/(\d+)', url)
        if match:
            return match.group(1)
        # Fallback: use URL hash
        return url.split("/")[-1].split("?")[0]
