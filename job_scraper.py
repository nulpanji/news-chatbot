import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

class JobScraper:
    def __init__(self):
        self.jobs = []
        self.base_url = "https://www.saramin.co.kr/zf_user/search/recruit"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_saramin(self, num_pages=3):
        """Scrape job postings from Saramin"""
        print("Scraping Saramin...")
        
        try:
            for page in range(1, num_pages + 1):
                print(f"Fetching page {page}...")
                
                params = {
                    'searchword': '대구 시니어',  # Search for "Daegu Senior"
                    'recruitPage': page,
                    'recruitSort': 'relation',
                    'recruitPageCount': 40,
                    'inner_com_type': 'scale',
                    'company_cd': 0,
                    'quick_apply': '',
                    'except_read': '',
                }
                
                try:
                    # Add random delay between requests
                    time.sleep(random.uniform(2, 4))
                    
                    response = requests.get(self.base_url, params=params, headers=self.headers)
                    print(f"Page {page} status: {response.status_code}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Check for no results message
                        no_result = soup.find('div', class_='no_result')
                        if no_result:
                            print("No jobs found matching the criteria")
                            break
                        
                        # Find all job posts
                        job_list = soup.find('div', class_='content')
                        if job_list:
                            jobs = job_list.find_all('div', class_='item_recruit')
                            print(f"Found {len(jobs)} jobs on page {page}")
                            
                            for job in jobs:
                                try:
                                    # Extract job information
                                    title_elem = job.find('h2', class_='job_tit')
                                    company_elem = job.find('strong', class_='corp_name')
                                    location_elem = job.find('div', class_='job_condition')
                                    
                                    title = title_elem.text.strip() if title_elem else "N/A"
                                    company = company_elem.text.strip() if company_elem else "N/A"
                                    
                                    # Get location and requirements
                                    conditions = []
                                    if location_elem:
                                        conditions = [span.text.strip() for span in location_elem.find_all('span')]
                                    
                                    location = conditions[0] if len(conditions) > 0 else "N/A"
                                    experience = conditions[1] if len(conditions) > 1 else "N/A"
                                    education = conditions[2] if len(conditions) > 2 else "N/A"
                                    
                                    # Get the job URL
                                    url = ""
                                    if title_elem and title_elem.find('a'):
                                        url = "https://www.saramin.co.kr" + title_elem.find('a')['href']
                                    
                                    job_info = {
                                        'source': 'Saramin',
                                        'title': title,
                                        'company': company,
                                        'location': location,
                                        'experience': experience,
                                        'education': education,
                                        'url': url,
                                        'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }
                                    
                                    self.jobs.append(job_info)
                                    print(f"Found job: {title} at {company}")
                                    
                                except Exception as e:
                                    print(f"Error parsing job: {str(e)}")
                                    continue
                        else:
                            print("No job listings found on this page")
                            
                except requests.exceptions.RequestException as e:
                    print(f"Error making request: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Saramin: {str(e)}")
            
    def save_jobs(self):
        """Save scraped jobs to a JSON file"""
        if not self.jobs:
            print("No jobs to save")
            return
            
        filename = f"daegu_senior_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.jobs, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(self.jobs)} jobs to {filename}")
        except Exception as e:
            print(f"Error saving jobs: {str(e)}")

if __name__ == "__main__":
    scraper = JobScraper()
    scraper.scrape_saramin()
    scraper.save_jobs()
