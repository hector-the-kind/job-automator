from app.scrapers.base import BaseScraper


class WellfoundScraper(BaseScraper):
    """Scraper for Wellfound (AngelList) India."""
    
    portal_name = "wellfound"
    base_url = "https://wellfound.com"
    
    async def search(self, query: str, location: str = "India", page: int = 1) -> list[dict]:
        """Search Wellfound jobs."""
        context = await self._get_browser()
        page_obj = await context.new_page()
        
        try:
            # Wellfound job search URL
            url = f"{self.base_url}/jobs?role={query.replace(' ', '+')}&location={location.replace(' ', '+')}"
            
            await page_obj.goto(url, wait_until="networkidle", timeout=30000)
            await self._random_delay()
            
            # Extract job cards
            jobs = await page_obj.evaluate("""
                () => {
                    const cards = document.querySelectorAll('[data-test="StartupResult"]');
                    return Array.from(cards).map(card => {
                        const titleEl = card.querySelector('h2');
                        const companyEl = card.querySelector('a[data-test="StartupResult-StartupName"]');
                        const locationEl = card.querySelector('[data-test="StartupResult-Location"]');
                        const salaryEl = card.querySelector('[data-test="StartupResult-Salary"]');
                        const linkEl = card.querySelector('a[data-test="StartupResult-StartupName"]');
                        
                        return {
                            title: titleEl?.textContent?.trim() || '',
                            company: companyEl?.textContent?.trim() || '',
                            location: locationEl?.textContent?.trim() || '',
                            salary: salaryEl?.textContent?.trim() || '',
                            url: linkEl ? `https://wellfound.com${linkEl.getAttribute('href')}` : '',
                        };
                    }).filter(job => job.title);
                }
            """)
            
            # Enrich jobs
            for i, job in enumerate(jobs):
                job["portal"] = self.portal_name
                job["portal_job_id"] = f"wellfound_{page}_{i}"
                job["is_remote"] = "remote" in (job.get("location", "").lower())
                job["is_hybrid"] = "hybrid" in (job.get("location", "").lower())
                
                salary_min, salary_max = self.parse_salary(job.pop("salary", ""))
                job["salary_min"] = salary_min
                job["salary_max"] = salary_max
            
            return jobs
            
        except Exception as e:
            print(f"[Wellfound] Search error: {e}")
            return []
        finally:
            await page_obj.close()
    
    async def get_job_details(self, job_url: str) -> dict | None:
        """Get detailed job information."""
        context = await self._get_browser()
        page_obj = await context.new_page()
        
        try:
            await page_obj.goto(job_url, wait_until="networkidle", timeout=30000)
            await self._random_delay()
            
            details = await page_obj.evaluate("""
                () => {
                    const descEl = document.querySelector('.styles_jobDescription__SnMzU');
                    return {
                        description: descEl?.textContent?.trim() || '',
                    };
                }
            """)
            
            return details
            
        except Exception as e:
            print(f"[Wellfound] Details error: {e}")
            return None
        finally:
            await page_obj.close()
