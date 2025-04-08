"""
CareerViet Job Scraper

This module handles scraping job listings from CareerViet website using Selenium.
"""
import os
import time
import random
import re
import pandas as pd
import threading
import concurrent.futures
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Thread-local storage for WebDriver instances
thread_local = threading.local()

class CareerVietScraper:
    """Scraper for CareerViet job listings."""
    
    def __init__(self, chrome_driver_path=None, max_workers=4, max_jobs_per_page=50, max_jobs=500):
        """
        Initialize the CareerViet scraper.
        
        Args:
            chrome_driver_path: Path to Chrome WebDriver (if not in PATH)
            max_workers: Maximum number of concurrent workers
            max_jobs_per_page: Maximum number of jobs to scrape per page
            max_jobs: Maximum total jobs to scrape
        """
        # Add Selenium driver to PATH if provided
        if chrome_driver_path:
            os.environ['PATH'] += os.pathsep + chrome_driver_path
            
        self.max_workers = max_workers
        self.max_jobs_per_page = max_jobs_per_page
        self.max_jobs = max_jobs
    
    @staticmethod
    def get_driver():
        """Create or return thread-local driver with enhanced settings."""
        if not hasattr(thread_local, "driver"):
            options = ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--blink-settings=imagesEnabled=false')  # Disable images
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            
            # Set a realistic user agent
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            thread_local.driver = webdriver.Chrome(options=options)
            thread_local.driver.set_page_load_timeout(30)  # Increased timeout
        return thread_local.driver
    
    @staticmethod
    def generate_pagination_urls(base_url, max_page=10):
        """
        Generate consistent pagination URLs for CareerViet.
        
        Args:
            base_url: Base URL for the job search
            max_page: Maximum number of pages to scrape
            
        Returns:
            List of paginated URLs
        """
        print(f"Generating pagination URLs from {base_url}")
        
        # Handle the first page (base URL)
        urls = [base_url]
        
        # Extract the pattern to ensure consistent URLs
        if base_url.endswith('-vi.html') and 'trang-' not in base_url:
            # First page URL, generate subsequent pages
            base_part = base_url.split('-vi.html')[0]
            
            # Generate the remaining page URLs
            for page in range(2, max_page + 1):
                page_url = f"{base_part}-trang-{page}-vi.html"
                urls.append(page_url)
        
        # Handle the case where the base URL already includes a page number
        elif 'trang-' in base_url:
            match = re.search(r'(.*)-trang-\d+(-vi\.html)', base_url)
            if match:
                base_part = match.group(1)
                suffix = match.group(2)
                
                # Add the first page URL
                first_page_url = f"{base_part}-vi.html"
                urls = [first_page_url]
                
                # Add remaining pages
                for page in range(2, max_page + 1):
                    page_url = f"{base_part}-trang-{page}-vi.html"
                    urls.append(page_url)
        
        return urls
    
    @staticmethod
    def get_soup(url, wait_time=5, scroll_times=4, retries=2):
        """
        Get BeautifulSoup object from URL with optimized settings and retries.
        
        Args:
            url: Page URL to scrape
            wait_time: Time to wait for elements to load
            scroll_times: Number of times to scroll the page
            retries: Number of retries if unsuccessful
            
        Returns:
            BeautifulSoup object or None if unsuccessful
        """
        for attempt in range(retries + 1):
            try:
                driver = CareerVietScraper.get_driver()
                driver.get(url)
                
                # Set a reasonable implicit wait
                driver.implicitly_wait(wait_time)
                
                # Try to explicitly wait for job items to load
                try:
                    WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "job-item"))
                    )
                except TimeoutException:
                    print(f"Timeout waiting for job items on {url}")
                
                # Scroll down to load lazy content
                for i in range(scroll_times):
                    driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {(i+1)/scroll_times});")
                    time.sleep(0.8)  # Delay between scrolls
                
                # Final scrolls to ensure all content is loaded
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(0.5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                html_content = driver.page_source
                return BeautifulSoup(html_content, 'html.parser')
                
            except Exception as e:
                if attempt < retries:
                    wait_secs = (attempt + 1) * 2  # Progressive backoff
                    print(f"Error getting soup for {url}: {e}. Retrying in {wait_secs}s... (Attempt {attempt+1}/{retries})")
                    time.sleep(wait_secs)
                else:
                    print(f"Failed to get soup for {url} after {retries} retries: {e}")
                    return None
    
    @staticmethod
    def extract_text_safely(element):
        """
        Extract text from an element with proper error handling.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Extracted text or empty string if unsuccessful
        """
        if element is None:
            return ""
        
        try:
            # Get text with proper spacing between elements
            text = element.get_text(separator=' ', strip=True)
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def get_job_details(self, job_url):
        """
        Extract detailed job information from job detail page.
        
        Args:
            job_url: URL of the job details page
            
        Returns:
            Dictionary with job details
        """
        job_id = job_url.split('/')[-1]
        print(f"Scraping details: {job_id}")
        
        try:
            # Get the soup for the job detail page with increased wait time
            job_soup = self.get_soup(job_url, wait_time=8, scroll_times=5, retries=2)
            
            if job_soup is None:
                return self._get_empty_job_details()
            
            # Extract job metadata
            job_level, job_type, experience, industry = self._extract_job_metadata(job_soup)
            
            # Extract job description and requirements
            description_content = self._extract_job_description(job_soup)
            requirements_content = self._extract_job_requirements(job_soup, description_content)
            
            return {
                "Job Description": description_content,
                "Job Requirements": requirements_content,
                "Job Level": job_level,
                "Job Type": job_type,
                "Experience": experience,
                "Industry": industry
            }
            
        except Exception as e:
            print(f"Error getting job details: {e}")
            return self._get_empty_job_details(error=str(e))
    
    def _get_empty_job_details(self, error=None):
        """Return empty job details."""
        msg = "Could not load job details"
        if error:
            msg = f"Error retrieving: {error}"
            
        return {
            "Job Description": msg,
            "Job Requirements": msg,
            "Job Level": "Not available",
            "Job Type": "Not available", 
            "Experience": "Not available",
            "Industry": "Not available"
        }
    
    def _extract_job_metadata(self, job_soup):
        """Extract job metadata (level, type, experience, industry)."""
        job_level = "Not available"
        job_type = "Not available"
        experience = "Not available"
        industry = "Not available"
        
        # Try to find elements containing the job metadata using various selectors
        job_info_selectors = [
            'div.job-info', 'ul.job-meta', 'div.job-metadata', 
            'div.job-overview', 'ul.overview-items', 'div.job-details',
            'div.meta-job-detail', 'div.detail-box', 'div.detail-content',
            'div.job-detail-content'
        ]
        
        job_info_element = None
        for selector in job_info_selectors:
            job_info_element = job_soup.select_one(selector)
            if job_info_element:
                break
        
        if job_info_element:
            metadata_items = job_info_element.find_all(['li', 'div', 'span'])
            
            for item in metadata_items:
                item_text = self.extract_text_safely(item).lower()
                
                # Check for job level
                if any(term in item_text for term in ['cấp bậc', 'chức vụ', 'level', 'position level']):
                    match = re.search(r'(?:cấp bậc|chức vụ|level|position level)[:\s]+(.*?)(?=$|[•\-\,\.])', item_text, re.IGNORECASE)
                    if match:
                        job_level = match.group(1).strip()
                
                # Check for job type
                if any(term in item_text for term in ['hình thức', 'job type', 'employment type']):
                    match = re.search(r'(?:hình thức|job type|employment type)[:\s]+(.*?)(?=$|[•\-\,\.])', item_text, re.IGNORECASE)
                    if match:
                        job_type = match.group(1).strip()
                
                # Check for experience
                if any(term in item_text for term in ['kinh nghiệm', 'experience']):
                    match = re.search(r'(?:kinh nghiệm|experience)[:\s]+(.*?)(?=$|[•\-\,\.])', item_text, re.IGNORECASE)
                    if match:
                        experience = match.group(1).strip()
                
                # Check for industry
                if any(term in item_text for term in ['ngành nghề', 'industry', 'field']):
                    match = re.search(r'(?:ngành nghề|industry|field)[:\s]+(.*?)(?=$|[•\-\,\.])', item_text, re.IGNORECASE)
                    if match:
                        industry = match.group(1).strip()
        
        # Try additional methods if data is still missing
        if job_level == "Not available" or job_type == "Not available" or experience == "Not available" or industry == "Not available":
            # Method 2: Look for table-based format with metadata
            for table in job_soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 2:
                        header = self.extract_text_safely(cells[0]).lower()
                        value = self.extract_text_safely(cells[1])
                        
                        if any(term in header for term in ['cấp bậc', 'chức vụ', 'level']):
                            job_level = value
                        elif any(term in header for term in ['hình thức', 'job type']):
                            job_type = value
                        elif any(term in header for term in ['kinh nghiệm', 'experience']):
                            experience = value
                        elif any(term in header for term in ['ngành nghề', 'industry']):
                            industry = value
            
            # Method 3: Look for specific structured divs with labels and values
            label_elements = job_soup.find_all(['strong', 'b', 'label', 'dt'])
            
            for label_elem in label_elements:
                label_text = self.extract_text_safely(label_elem).lower()
                
                # Try to find the corresponding value
                value_elem = label_elem.next_sibling
                if not value_elem or not value_elem.string:
                    # Try parent's next sibling
                    if label_elem.parent:
                        value_elem = label_elem.parent.next_sibling
                
                if value_elem:
                    value = self.extract_text_safely(value_elem)
                    
                    # If value is empty, try to get the next element's text
                    if not value and hasattr(value_elem, 'next'):
                        next_elem = value_elem.next
                        if next_elem:
                            value = self.extract_text_safely(next_elem)
                    
                    # Clean value (remove the label text if it got included)
                    value = value.replace(label_text, '').strip(': \t\n-')
                    
                    if any(term in label_text for term in ['cấp bậc', 'chức vụ', 'level']) and job_level == "Not available":
                        job_level = value
                    elif any(term in label_text for term in ['hình thức', 'job type']) and job_type == "Not available":
                        job_type = value
                    elif any(term in label_text for term in ['kinh nghiệm', 'experience']) and experience == "Not available":
                        experience = value
                    elif any(term in label_text for term in ['ngành nghề', 'industry']) and industry == "Not available":
                        industry = value
        
        return job_level, job_type, experience, industry
    
    def _extract_job_description(self, job_soup):
        """Extract job description."""
        description_content = ""
        
        # Method 1: Try common selectors
        desc_selectors = [
            'div.job-description', 'div.job-detail-content', 'div.content-tab', 
            'div#job-description', '.job-content', '.detail-content', '.job-detail',
            'div.description', 'div.job-info', '.job-overview', 'div.job-data',
            '.job-details-content', 'article.job-content', 'section.job-detail'
        ]
        
        for selector in desc_selectors:
            desc_elem = job_soup.select_one(selector)
            if desc_elem:
                description_content = self.extract_text_safely(desc_elem)
                if len(description_content) > 100:  # Ensure we have substantial content
                    break
        
        # Method 2: Look for description-related headings
        if not description_content or len(description_content) < 100:
            desc_headings = ['mô tả công việc', 'job description', 'about the job', 'job brief', 'job details']
            for heading in job_soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b']):
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in desc_headings):
                    # Extract content until next heading or significant boundary
                    section_content = []
                    current = heading.next_sibling
                    
                    while current:
                        if current.name in ['h1', 'h2', 'h3', 'h4', 'strong', 'b']:
                            next_heading_text = self.extract_text_safely(current).lower()
                            # Stop if we reach a section that's not part of the description
                            if any(term in next_heading_text for term in ['yêu cầu', 'requirements', 'qualifications', 'benefits', 'quyền lợi']):
                                break
                                
                        if current.name:  # If it's an element node
                            content = self.extract_text_safely(current)
                            if content:
                                section_content.append(content)
                        current = current.next_sibling
                        
                    if section_content:
                        description_content = " ".join(section_content)
                        break
        
        # Method 3: Fall back to analyzing the largest text blocks
        if not description_content or len(description_content) < 100:
            paragraphs = job_soup.find_all(['p', 'div', 'section'])
            paragraphs = [p for p in paragraphs if len(self.extract_text_safely(p)) > 50]  # Substantial paragraphs
            
            if paragraphs:
                # Sort by length and use the longest paragraphs
                paragraphs.sort(key=lambda p: len(self.extract_text_safely(p)), reverse=True)
                description_content = "\n".join([self.extract_text_safely(p) for p in paragraphs[:3]])
        
        # Clean up and format the extracted content
        description_content = re.sub(r'\s+', ' ', description_content).strip()
        
        # Ensure content has minimum substance
        if not description_content or len(re.findall(r'[a-zA-Z]', description_content)) < 20:
            description_content = "Description unavailable or could not be extracted properly"
        
        return description_content
    
    def _extract_job_requirements(self, job_soup, description_content=""):
        """Extract job requirements."""
        requirements_content = ""
        
        # Method 1: Try dedicated requirements section
        req_selectors = [
            'div.job-requirements', 'div#job-requirements', '.requirements', 
            'div.qualifications', 'div.candidate-profile', '.required-skills',
            '#qualifications', 'div.skill-requirements', '.candidate-requirements'
        ]
        
        for selector in req_selectors:
            req_elem = job_soup.select_one(selector)
            if req_elem:
                requirements_content = self.extract_text_safely(req_elem)
                if len(requirements_content) > 50:  # Ensure we have substantial content
                    break
        
        # Method 2: Try to find sections with requirement-related headings
        if not requirements_content or len(requirements_content) < 50:
            req_headings = ['yêu cầu', 'requirements', 'qualifications', 'skills', 'experience required', 
                          'what we\'re looking for', 'candidate requirements', 'kỹ năng']
            
            for heading in job_soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b']):
                heading_text = self.extract_text_safely(heading).lower()
                if any(term in heading_text for term in req_headings):
                    # Extract content until next heading or significant boundary
                    section_content = []
                    current = heading.next_sibling
                    
                    while current:
                        if current.name in ['h1', 'h2', 'h3', 'h4', 'strong', 'b']:
                            next_heading_text = self.extract_text_safely(current).lower()
                            # Stop if we reach a section that's not part of requirements
                            if any(term in next_heading_text for term in ['benefits', 'quyền lợi', 'how to apply', 'nộp hồ sơ']):
                                break
                                
                        if current.name:  # If it's an element node
                            content = self.extract_text_safely(current)
                            if content:
                                section_content.append(content)
                        current = current.next_sibling
                        
                    if section_content:
                        requirements_content = " ".join(section_content)
                        break
        
        # Method 3: Extract from description using regex pattern matching
        if not requirements_content and description_content:
            # Look for requirement sections within the description
            desc_lower = description_content.lower()
            
            # Common requirement section starters
            patterns = [
                r'(?:yêu cầu|requirements|qualifications|what we\'re looking for)[\s\:]+(.*?)(?:quyền lợi|benefits|what we offer|how to apply|$)',
                r'(?:kỹ năng|skills required|experience needed)[\s\:]+(.*?)(?:quyền lợi|benefits|what we offer|how to apply|$)'
            ]
            
            for pattern in patterns:
                matches = re.search(pattern, desc_lower, re.DOTALL)
                if matches:
                    # Get the matched content
                    req_text = matches.group(1).strip()
                    # Format as a bullet list if it contains bullet-like patterns
                    if re.search(r'[•\-\*]', req_text):
                        requirements_content = req_text
                        break
        
        # Clean up and format the extracted content
        requirements_content = re.sub(r'\s+', ' ', requirements_content).strip()
        
        if not requirements_content or len(re.findall(r'[a-zA-Z]', requirements_content)) < 20:
            # If requirements weren't found separately, try to extract from description
            if "yêu cầu:" in description_content.lower() or "requirements:" in description_content.lower():
                requirements_content = "Requirements included in job description"
            else:
                requirements_content = "Requirements unavailable or could not be extracted properly"
        
        return requirements_content
    
    def process_job(self, job):
        """
        Process a single job listing.
        
        Args:
            job: BeautifulSoup element for a job
            
        Returns:
            Dictionary with job data or None if unsuccessful
        """
        try:
            title_tag = job.find('div', class_="title")
            title=title_tag.text.strip().replace('\n', '').replace('(Mới)', '').replace('  ', '')
            company_tag = job.find('a', class_="company-name")
            company=company_tag.text.strip() if company_tag else "Company not found" if title_tag else "Title not found"
            link_tag = job.find('a', class_="job_link")
            link = link_tag.get('href') if link_tag else "Link not found"
            
            # Make sure link is absolute URL
            if link.startswith('/'):
                link = "https://careerviet.vn" + link
            
            location_tag = job.find('div', class_="location")
            location = location_tag.text.strip() if location_tag else "Location not found"

            salary_tag = job.find('div', class_="salary")
            salary = salary_tag.text.replace('Lương:', '').strip() if salary_tag else "Salary not found"

            time_class = job.find('div', class_="time")
                        
            if time_class:
                # For update time
                update_time = "Update time not found"
                for li in time_class.find_all('li'):
                    if "Cập nhật" in li.text:
                        update_time = li.find('time').text.strip() if li.find('time') else update_time
                        break
                        
                # For expire time
                expire_time = "Expire date not found"
                for li in time_class.find_all('li'):
                    if "Hạn nộp" in li.text:
                        expire_time = li.find('time').text.strip() if li.find('time') else expire_time
                        break
            else:
                update_time = "Update time not found"
                expire_time = "Expire date not found"
                
            welfare_ul = job.find('ul', class_='welfare')
            welfare_items = [li.text.strip() for li in welfare_ul.find_all('li')] if welfare_ul else []

            # Get detailed job information
            job_details = self.get_job_details(link)  if link != "Link not found" else {}

            job_data = {
                "Job Title": title,
                "Company": company,
                "Location": location,
                "Salary": salary,
                "Date": update_time,
                "Job Link": link,
                "Expire Date": expire_time,
                "Welfare": welfare_items,
                "Job Description": job_details["Job Description"],
                "Job Requirements": job_details["Job Requirements"],
                "Job Level": job_details["Job Level"],
                "Job Type": job_details["Job Type"],
                "Experience": job_details["Experience"],
                "Industry": job_details["Industry"]
            }
            return job_data
            
        except Exception as e:
            print(f"Error processing job: {e}")
            return None
    
    def get_jobs_from_page(self, page_url):
        """
        Get jobs from a page with enhanced reliability.
        
        Args:
            page_url: URL of the page to scrape
            
        Returns:
            List of job data dictionaries
        """
        print(f"\nScraping page: {page_url}")
        
        # Try multiple scrolling approaches to maximize job collection
        soup = self.get_soup(page_url, wait_time=10, scroll_times=7, retries=2)

        if soup is None:
            print(f"Failed to get soup for page: {page_url}")
            return []

        # Look for job listings
        job_list = soup.find_all('div', class_=["job-item", "job-item has-badge"])
        print(f"Found {len(job_list)} job listings on this page")

        # If fewer than expected, try with a direct browser approach
        if len(job_list) < self.max_jobs_per_page:
            print(f"Fewer jobs than expected ({len(job_list)} < {self.max_jobs_per_page}). Trying direct browser approach...")
            
            try:
                driver = self.get_driver()
                driver.get(page_url)
                
                # Wait for job items to load
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-item"))
                )
                
                # More aggressive scrolling
                for i in range(10):
                    driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {(i+1)/10});")
                    time.sleep(1)
                
                # Final scroll to bottom and wait
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if there's a "Show more" or "Load more" button and click it
                try:
                    load_more_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'more')]")
                    for button in load_more_buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            time.sleep(2)
                            print("Clicked 'Load more' button")
                except Exception as e:
                    print(f"No load more button or error: {e}")
                
                # Get the updated page source
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Look for job listings again
                job_list = soup.find_all('div', class_=["job-item", "job-item has-badge"])
                print(f"After aggressive scrolling, found {len(job_list)} job listings")
                
            except Exception as e:
                print(f"Error in direct browser approach: {e}")
        
        # Take up to max_jobs_per_page jobs
        jobs_to_process = job_list[:self.max_jobs_per_page]
        print(f"Processing {len(jobs_to_process)} jobs (out of {len(job_list)} found)")
        
        # Track job IDs or links to detect duplicates on the same page
        seen_job_ids = set()
        
        # Process jobs from this page and return the results
        results = []
        for job in jobs_to_process:
            # Extract job ID or link to check for duplicates
            link_tag = job.find('a', class_="job_link")
            job_link = link_tag.get('href') if link_tag else None
            
            # Skip if we've already seen this job on this page
            if not job_link or job_link in seen_job_ids:
                continue
                
            seen_job_ids.add(job_link)
            
            job_data = self.process_job(job)
            if job_data:
                results.append(job_data)
                # Add a small delay to avoid rate limiting
                time.sleep(random.uniform(0.1, 0.3))
        
        print(f"Successfully processed {len(results)} jobs from this page")
        return results
    
    def scrape(self, base_url, max_pages=10):
        """
        Scrape job data from multiple pages with multithreading.
        
        Args:
            base_url: Base URL for job search
            max_pages: Maximum number of pages to scrape
            
        Returns:
            Pandas DataFrame with scraped job data
        """
        start_time = time.time()
        
        # Generate pagination URLs
        all_pages = self.generate_pagination_urls(base_url, max_page=max_pages)
        print(f"Found {len(all_pages)} pages to scrape")
        
        all_jobs = []
        total_jobs_needed = min(self.max_jobs, self.max_jobs_per_page * len(all_pages))
        
        print(f"Starting multithreaded scraping with {self.max_workers} workers for up to {total_jobs_needed} jobs from {len(all_pages)} pages...")
        
        # Track processed job links to avoid duplicates
        processed_job_links = set()
        
        # Use ThreadPoolExecutor to process pages in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all page processing tasks
            future_to_page = {
                executor.submit(self.get_jobs_from_page, page): page 
                for page in all_pages
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    page_jobs = future.result()
                    
                    print(f"\nProcessing results from page: {page}")
                    print(f"Got {len(page_jobs)} jobs from this page")
                    
                    # Add only non-duplicate jobs
                    new_jobs_count = 0
                    for job in page_jobs:
                        job_link = job.get('Job Link', '')
                        if job_link and job_link not in processed_job_links:
                            processed_job_links.add(job_link)
                            all_jobs.append(job)
                            new_jobs_count += 1
                    
                    print(f"Added {new_jobs_count} new unique jobs from this page")
                    print(f"Total unique jobs so far: {len(all_jobs)}")
                    
                    # If we have enough jobs already, cancel remaining futures
                    if len(all_jobs) >= self.max_jobs:
                        print(f"Reached target of {self.max_jobs} jobs, cancelling remaining tasks")
                        for f in future_to_page:
                            if not f.done():
                                f.cancel()
                        break
                except Exception as e:
                    print(f"Error processing page {page}: {e}")
        
        # Clean up thread-local drivers
        try:
            for thread in threading.enumerate():
                if hasattr(thread_local, "driver"):
                    try:
                        thread_local.driver.quit()
                    except:
                        pass
        except Exception as e:
            print(f"Error cleaning up drivers: {e}")
        
        # Final check to ensure data quality
        verified_jobs = []
        for job in all_jobs[:self.max_jobs]:
            # Ensure job description and requirements are valid
            if isinstance(job['Job Description'], str) and job['Job Description'] and \
               isinstance(job['Job Requirements'], str) and job['Job Requirements']:
                verified_jobs.append(job)
            else:
                print(f"Skipping job with invalid description/requirements: {job.get('Job Title', 'Unknown')}")
        
        print(f"\nCompleted scraping from all pages in {time.time() - start_time:.2f} seconds.")
        print(f"Total unique jobs collected: {len(all_jobs)}")
        print(f"Final result: {len(verified_jobs)} valid jobs")
        
        return pd.DataFrame(verified_jobs)
    
    def save_to_csv(self, df, filename="careerviet_jobs.csv"):
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        # Ensure the Job Description and Job Requirements are properly formatted strings
        for col in ['Job Description', 'Job Requirements']:
            df[col] = df[col].astype(str)
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Data saved to {filename}")
        return filename
    
    def save_to_excel(self, df, filename="careerviet_jobs.xlsx"):
        """
        Save DataFrame to Excel file.
        
        Args:
            df: DataFrame to save
            filename: Output filename
            
        Returns:
            Path to saved file or None if unsuccessful
        """
        try:
            # Ensure the Job Description and Job Requirements are properly formatted strings
            for col in ['Job Description', 'Job Requirements']:
                df[col] = df[col].astype(str)
            
            df.to_excel(filename, index=False)
            print(f"Data saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            print("If you're missing required packages, try: pip install openpyxl")
            return None