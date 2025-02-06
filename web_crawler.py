import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import os

class WebsiteCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.queue = []
        self.results = []
        self.crawl_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept-Encoding': 'gzip'
        })
        
        # CSV configuration
        self.csv_file = 'crawl_results.csv'
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Page URL', 
                    'Broken Links (Status Codes)', 
                    'Script Errors', 
                    'Responsiveness Issues', 
                    'Timestamp'
                ])

    def check_responsiveness(self, soup):
        issues = []
        viewports = ['mobile', 'tablet', 'desktop']
        for viewport in viewports:
            for tag in soup.find_all(['div', 'section', 'main']):
                if tag.has_attr('style') and 'overflow' in tag['style']:
                    issues.append(f"{viewport} viewport: {tag.name} overflow")
                    if len(issues) >= 20:  # Limit issues
                        break
        return '; '.join(issues)

    def check_links(self, soup, base_url):
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href'].split('#')[0].strip()
            if not href or href.startswith('javascript:'):
                continue
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            if parsed.netloc == urlparse(self.base_url).netloc:
                links.append(full_url)
        return list(set(links))

    def process_url(self, url):
        try:
            # Get current timestamp first
            current_time = datetime.now().strftime('%m/%d/%Y %H:%M')
            
            response = self.session.get(url, timeout=10)
            self.crawl_count += 1
            print(f"Crawled: {self.crawl_count} | Current: {url[:60]}...")

            soup = BeautifulSoup(response.content, 'lxml')
            
            # Broken links with status codes
            broken_links = []
            links = self.check_links(soup, url)[:20]  # Check first 20 links
            
            for link in links:
                try:
                    res = self.session.head(
                        link, 
                        timeout=5, 
                        allow_redirects=True
                    )
                    if res.status_code >= 400:
                        broken_links.append(
                            f"{link} ({res.status_code})"
                        )
                except Exception as e:
                    # Log connection errors without status codes separately
                    broken_links.append(
                        f"{link} (Connection Error: {str(e)[:30]})"
                    )

            # Responsiveness issues
            responsiveness_issues = self.check_responsiveness(soup)

            # Store results with guaranteed timestamp
            self.results.append({
                'Page URL': url,
                'Broken Links (Status Codes)': '; '.join(broken_links[:10]),
                'Script Errors': 'N/A (JS disabled)', 
                'Responsiveness Issues': responsiveness_issues,
                'Timestamp': current_time  # Use pre-generated timestamp
            })

            # Add new URLs to queue
            new_urls = [
                link for link in links 
                if link not in self.visited_urls
            ]
            self.visited_urls.update(new_urls)
            self.queue.extend(new_urls)

            # Save progress every 25 URLs
            if len(self.results) >= 25:
                self.save_results()

        except Exception as e:
            # Log failed URLs with timestamp
            self.results.append({
                'Page URL': url,
                'Broken Links (Status Codes)': '',
                'Script Errors': f"Page load error: {str(e)[:50]}",
                'Responsiveness Issues': '',
                'Timestamp': current_time
            })
            print(f"Error crawling {url}: {str(e)[:50]}")

    def save_results(self):
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'Page URL', 
                    'Broken Links (Status Codes)', 
                    'Script Errors', 
                    'Responsiveness Issues', 
                    'Timestamp'
                ])
                writer.writerows(self.results)
            self.results = []
            print(f"Saved progress (Total: {self.crawl_count})")
        except Exception as e:
            print(f"CSV Save Error: {str(e)}")

    def start_crawl(self, max_urls=5000):
        self.queue.append(self.base_url)
        self.visited_urls.add(self.base_url)
        
        while self.queue and self.crawl_count < max_urls:
            url = self.queue.pop(0)
            self.process_url(url)
        
        # Final save
        if self.results:
            self.save_results()
        print(f"Crawling complete! Total: {self.crawl_count} pages")

if __name__ == '__main__':
    crawler = WebsiteCrawler('https://softwarefinder.com')
    crawler.start_crawl(max_urls=5000)