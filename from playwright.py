import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
import os

class WebsiteCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.queue = []
        self.results = []
        self.crawl_count = 0
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip'})
        
        # CSV configuration
        self.csv_file = 'crawl_results.csv'
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Page URL', 'Broken Links', 'Script Errors', 
                               'Responsiveness Issues', 'Timestamp'])

    def check_responsiveness(self, soup):
        issues = []
        for tag in soup.find_all(['div', 'section', 'main']):
            if tag.has_attr('style') and 'overflow' in tag['style']:
                issues.append(f"{tag.name} overflow")
                if len(issues) >= 20:  # Limit to 20 issues/page
                    break
        return '; '.join(issues)

    def check_links(self, soup, base_url):
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href'].split('#')[0]  # Ignore anchor links
            full_url = urljoin(base_url, href).rstrip('/')
            parsed = urlparse(full_url)
            if parsed.netloc == urlparse(self.base_url).netloc:
                links.append(full_url)
        return list(set(links))  # Deduplicate

    def process_url(self, url):
        try:
            # Fast timeout configuration
            response = self.session.get(url, timeout=(3, 6))
            self.crawl_count += 1
            print(f"Crawled: {self.crawl_count} pages | Current: {url[:60]}...")

            soup = BeautifulSoup(response.content, 'lxml')  # Faster parser

            # Broken links check (limited to 20 links/page)
            broken_links = []
            links = self.check_links(soup, url)[:20]
            for link in links:
                try:
                    res = self.session.head(link, timeout=3, allow_redirects=True)
                    if res.status_code >= 400:
                        broken_links.append(f"{link} ({res.status_code})")
                except Exception as e:
                    broken_links.append(f"{link} (Error: {str(e)[:30]})")

            # Store results
            self.results.append({
                'Page URL': url,
                'Broken Links': '; '.join(broken_links[:5]),  # Limit to 5 broken links
                'Script Errors': 'N/A (Disabled)', 
                'Responsiveness Issues': self.check_responsiveness(soup),
                'Timestamp': datetime.now().strftime('%m/%d/%Y %H:%M')
            })

            # Add new URLs to queue
            new_urls = [link for link in links if link not in self.visited_urls]
            self.visited_urls.update(new_urls)
            self.queue.extend(new_urls)

            # Save progress every 25 URLs (optimized for low memory)
            if len(self.results) >= 25:
                self.save_results()

        except Exception as e:
            print(f"Error crawling {url}: {str(e)[:50]}")

    def save_results(self):
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Page URL', 'Broken Links', 
                                                     'Script Errors', 'Responsiveness Issues', 
                                                     'Timestamp'],
                                      quoting=csv.QUOTE_MINIMAL)
                writer.writerows(self.results)
            self.results = []
            print(f"Saved progress (Total crawled: {self.crawl_count})")
        except Exception as e:
            print(f"CSV Save Error: {str(e)}")

    def start_crawl(self, max_runtime_hours=5):
        self.queue.append(self.base_url)
        self.visited_urls.add(self.base_url)
        
        start_time = time.time()
        max_runtime_seconds = max_runtime_hours * 3600  # Convert hours to seconds
        
        while self.queue:
            # Check if max runtime is exceeded
            if time.time() - start_time > max_runtime_seconds:
                print(f"Max runtime of {max_runtime_hours} hours reached. Stopping crawl.")
                break

            url = self.queue.pop(0)
            self.process_url(url)
        
        # Final save
        if self.results:
            self.save_results()
        print(f"Crawling complete! Total pages crawled: {self.crawl_count}")

if __name__ == '__main__':
    crawler = WebsiteCrawler('https://softwarefinder.com')
    crawler.start_crawl(max_runtime_hours=5)  # Set max runtime to 5 hours