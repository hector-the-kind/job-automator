import asyncio
import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BaseScraper(ABC):
    """Base class for job portal scrapers."""
    
    portal_name: str = "base"
    
    # Rate limiting
    min_delay = 2.0
    max_delay = 5.0
    
    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
    
    async def _get_browser(self) -> BrowserContext:
        """Get or create a browser context with stealth settings."""
        if self._context and self._context.pages:
            return self._context
        
        if not self._playwright:
            self._playwright = await async_playwright().start()
        
        if not self._browser:
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ]
            )
        
        self._context = await self._browser.new_context(
            user_agent=self._get_random_user_agent(),
            viewport={"width": 1920, "height": 1080},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )
        
        # Inject stealth scripts
        await self._context.add_init_script("""
            delete Object.getPrototypeOf(navigator).webdriver;
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)
        
        return self._context
    
    async def _random_delay(self):
        """Add random delay to mimic human behavior."""
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)
    
    async def _human_type(self, page: Page, selector: str, text: str):
        """Type text with human-like delays."""
        element = page.locator(selector)
        await element.click()
        for char in text:
            await element.type(char, delay=random.uniform(50, 150))
            if random.random() < 0.1:  # Occasional pause
                await asyncio.sleep(random.uniform(0.3, 0.8))
    
    @abstractmethod
    async def search(self, query: str, location: str = "", page: int = 1) -> list[dict]:
        """Search for jobs on the portal. Returns list of job dicts."""
        pass
    
    @abstractmethod
    async def get_job_details(self, job_url: str) -> dict | None:
        """Get detailed job information from a job URL."""
        pass
    
    async def scrape(self, query: str, location: str = "Hyderabad", max_pages: int = 3) -> list[dict]:
        """Scrape jobs from the portal."""
        all_jobs = []
        
        for page_num in range(1, max_pages + 1):
            try:
                jobs = await self.search(query, location, page_num)
                all_jobs.extend(jobs)
                
                if not jobs:
                    break  # No more results
                
                await self._random_delay()
            except Exception as e:
                print(f"[{self.portal_name}] Error on page {page_num}: {e}")
                break
        
        return all_jobs
    
    async def close(self):
        """Clean up browser resources."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
    
    def _get_random_user_agent(self) -> str:
        """Return a random realistic user agent."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        ]
        return random.choice(user_agents)
    
    @staticmethod
    def parse_salary(salary_text: str) -> tuple[int | None, int | None]:
        """Parse salary text into min/max integers."""
        import re
        
        if not salary_text:
            return None, None
        
        # Remove currency symbols and spaces
        cleaned = salary_text.replace("₹", "").replace("$", "").replace(",", "").strip()
        
        # Try to find range pattern (e.g., "15-25 LPA", "1500000-2500000")
        range_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)', cleaned)
        if range_match:
            min_sal = float(range_match.group(1))
            max_sal = float(range_match.group(2))
            
            # Handle LPA (Lakhs Per Annum)
            if "lpa" in salary_text.lower():
                min_sal = int(min_sal * 100000)
                max_sal = int(max_sal * 100000)
            else:
                min_sal = int(min_sal)
                max_sal = int(max_sal)
            
            return min_sal, max_sal
        
        # Try single value
        single_match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
        if single_match:
            value = float(single_match.group(1))
            if "lpa" in salary_text.lower():
                value = int(value * 100000)
            else:
                value = int(value)
            return value, value
        
        return None, None
