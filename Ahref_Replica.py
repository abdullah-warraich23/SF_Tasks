'''
1. Properly detecting missing meta keywords/descriptions
2. 2Counting H1, H2, H3 tags
3. Capturing full meta descriptions and keywords
4. Performance Metrics:
5. Fast response times (0.6-1.0 seconds per URL)
6. All pages successfully loaded (Status Code 200)
7. HTTPS status checked
8. Content Analysis:
9. Missing alt tags counted
10. Broken images detected
11. CTA availability checked
12. Responsive design analysis for mobile/tablet/desktop
13. URL Coverage:
14. Main pages (/accounting-software, /marketing-software)
15. Review pages (/reviews, specific product reviews)
16. Product pages (Aha, Jira, Asana)
'''

import asyncio
import aiohttp
import csv
from datetime import datetime
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import sys
import logging
import psutil
from typing import Set, List, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class WebCrawler:
    def __init__(self, base_url: str, timeout_minutes: int = 60, batch_size: int = 100, max_concurrent: int = 30):
        self.base_url = self._normalize_url(base_url)
        self.visited: Set[str] = set()
        self.queue: List[str] = []
        self.all_urls: Set[str] = set()  # Track all unique URLs found
        self.results: List[Dict] = []
        self.csv_file = "Crawl_Report_Alpha.csv"
        self.start_time = None
        self.total_requests = 0
        self.failed_requests = 0
        self.timeout_minutes = timeout_minutes
        self.batch_size = batch_size
        self.rate_limiter = asyncio.Semaphore(max_concurrent)
        self.last_progress_time = time.time()
        self.last_processed_count = 0
        self.process = psutil.Process()
        self._init_csv()
        logging.info(f"Initialized crawler for {self.base_url}")

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to prevent duplicates"""
        parsed = urlparse(url)
        # Remove query parameters and fragments
        clean_path = re.sub(r'/+', '/', parsed.path.rstrip('/'))
        return f"{parsed.scheme}://{parsed.netloc.lower()}{clean_path}"

    def _should_crawl_url(self, url: str) -> bool:
        """More aggressive URL filtering"""
        parsed = urlparse(url)

        # Skip non-HTML resources
        if any(ext in parsed.path.lower() for ext in [
            '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.css', '.js',
            '.ico', '.xml', '.txt', '.doc', '.docx', '.xls', '.xlsx', '.mp3', '.mp4','.webm' #Added more extensions
        ]):
            return False

        # Skip URLs with query parameters or fragments
        if parsed.query or parsed.fragment:
            return False

        # Skip potential duplicate content
        if any(pattern in parsed.path.lower() for pattern in [
            '/page/', '/tag/', '/category/', '/author/',
            '/feed/', '/rss/', '/atom/', '/api/', '/wp-',
            '/print/', '/search/', '/comment/', '/trackback/' #Added more patterns
        ]):
            return False

        return True

    def _init_csv(self):
        """Initialize CSV with headers"""
        headers = [
            'URL', 'Status Code', 'HTTPS Status', 'Load Time Issues',
            'SEO Issues', 'Missing Alt Tags', 'Meta Description',
            'Meta Keywords', 'Broken Images', 'CTA Available',
            'H1 Count', 'H2 Count', 'H3 Count',
            'Mobile Responsive', 'Tablet Responsive', 'Desktop Responsive',
            'Date', 'Time', 'Processing Duration (s)'
        ]
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        logging.info("Created new crawl report CSV file")

    async def _check_image(self, session: aiohttp.ClientSession, img_url: str) -> bool:
        """Check if image is broken"""
        try:
            async with session.head(img_url, timeout=5) as response:
                return response.status >= 400
        except Exception as e:
            logging.warning(f"Failed to check image {img_url}: {str(e)}")
            return True

    def _get_memory_usage(self) -> str:
        """Get current memory usage"""
        memory_info = self.process.memory_info()
        return f"{memory_info.rss / 1024 / 1024:.1f}MB"

    def _log_progress(self):
        """Calculate and log detailed progress metrics"""
        current_time = time.time()
        time_diff = current_time - self.last_progress_time
        processed_diff = len(self.visited) - self.last_processed_count

        if time_diff >= 1:  # Update stats every second
            process_rate = processed_diff / time_diff
            total_remaining = len(self.queue)
            eta_seconds = total_remaining / process_rate if process_rate > 0 else 0
            memory_usage = self._get_memory_usage()

            elapsed_minutes = (current_time - self.start_time) / 60
            urls_per_minute = len(self.visited) / elapsed_minutes if elapsed_minutes > 0 else 0

            logging.info(
                f"Progress: {len(self.visited):,} processed, {len(self.queue):,} queued | "
                f"Rate: {process_rate:.1f} URLs/s ({urls_per_minute:.1f} URLs/min) | "
                f"Memory: {memory_usage} | "
                f"ETA: {eta_seconds/60:.1f} minutes"
            )

            self.last_progress_time = current_time
            self.last_processed_count = len(self.visited)

    async def process_url(self, session: aiohttp.ClientSession, url: str) -> Tuple[Dict, List[str]]:
        """Process a single URL and return its data and found links"""
        async with self.rate_limiter:  # Rate limit requests
            start_time = time.time()
            result = {
                'URL': url,
                'Status Code': 0,
                'HTTPS Status': 'Secure' if url.startswith('https') else 'Not Secure',
                'Load Time Issues': 'None',
                'SEO Issues': '',
                'Missing Alt Tags': 0,
                'Meta Description': '',
                'Meta Keywords': '',
                'Broken Images': 0,
                'CTA Available': 'No',
                'H1 Count': 0,
                'H2 Count': 0,
                'H3 Count': 0,
                'Mobile Responsive': '',
                'Tablet Responsive': '',
                'Desktop Responsive': '',
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Time': datetime.now().strftime('%H:%M:%S'),
                'Processing Duration (s)': 0
            }

            new_urls = []
            self.total_requests += 1

            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with session.get(url, timeout=timeout, allow_redirects=True) as response:
                    result['Status Code'] = response.status

                    # Only process HTML content
                    content_type = response.headers.get('Content-Type', '').lower()
                    if not content_type.startswith('text/html'):
                        return result, []

                    try:
                        html = await response.text()
                    except UnicodeDecodeError:
                        logging.warning(f"Unicode decode error for {url}")
                        return result, []

                    soup = BeautifulSoup(html, 'html.parser')

                    # Extract and normalize links first (most important)
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        try:
                            full_url = urljoin(url, href)
                            normalized_url = self._normalize_url(full_url)
                            if (normalized_url.startswith(self.base_url) and
                                self._should_crawl_url(full_url) and
                                normalized_url not in self.all_urls):
                                new_urls.append(normalized_url)
                                self.all_urls.add(normalized_url)
                        except Exception as e:
                            logging.warning(f"Error processing link {href}: {str(e)}")

                    # SEO Analysis
                    seo_issues = []
                    title = soup.find('title')
                    if not title or not title.text.strip():
                        seo_issues.append("Missing title")

                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    meta_desc_content = meta_desc.get('content', '').strip() if meta_desc else ''
                    if not meta_desc_content:
                        seo_issues.append("Missing meta description")
                    result['Meta Description'] = meta_desc_content[:200] if meta_desc_content else ''

                    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                    meta_keywords_content = meta_keywords.get('content', '').strip() if meta_keywords else ''
                    if not meta_keywords_content:
                        seo_issues.append("Missing meta keywords")
                    result['Meta Keywords'] = meta_keywords_content[:200] if meta_keywords_content else ''

                    # Heading counts
                    result['H1 Count'] = len(soup.find_all('h1'))
                    result['H2 Count'] = len(soup.find_all('h2'))
                    result['H3 Count'] = len(soup.find_all('h3'))
                    if result['H1 Count'] == 0:
                        seo_issues.append("Missing H1")
                    elif result['H1 Count'] > 1:
                        seo_issues.append("Multiple H1 tags")

                    result['SEO Issues'] = '; '.join(seo_issues) if seo_issues else 'No SEO issues'

                    # Image Analysis
                    images = soup.find_all('img')
                    result['Missing Alt Tags'] = len([img for img in images if not img.get('alt')])

                    # Check first 5 images only
                    img_urls = [urljoin(url, img.get('src', '')) for img in images[:5] if img.get('src')]
                    broken_count = 0
                    for img_url in img_urls:
                        if await self._check_image(session, img_url):
                            broken_count += 1
                    result['Broken Images'] = broken_count

                    # CTA Analysis
                    cta_patterns = ['sign up', 'get started', 'learn more', 'contact us', 'buy now']
                    for link in soup.find_all(['a', 'button']):
                        text = link.text.lower()
                        classes = ' '.join(link.get('class', [])).lower()
                        if any(pattern in text for pattern in cta_patterns) or 'cta' in classes:
                            result['CTA Available'] = 'Yes'
                            break

                    # Responsive Analysis
                    viewport = soup.find('meta', attrs={'name': 'viewport'})
                    responsive_classes = bool(re.search(r'class=["\'](.*?)(mobile|tablet|desktop|sm\-|md\-|lg\-)', str(soup)))
                    media_queries = bool(soup.find_all('style', string=re.compile('@media')))

                    result.update({
                        'Mobile Responsive': 'Responsive' if viewport else 'Not responsive',
                        'Tablet Responsive': 'Responsive' if media_queries else 'Not responsive',
                        'Desktop Responsive': 'Responsive' if responsive_classes else 'Not responsive'
                    })

            except asyncio.TimeoutError:
                result['Load Time Issues'] = 'Timeout'
                self.failed_requests += 1
                logging.error(f"Timeout error for {url}")
            except Exception as e:
                result['Load Time Issues'] = f'Error: {str(e)[:100]}'
                self.failed_requests += 1
                logging.error(f"Failed to process {url}: {str(e)}")

            result['Processing Duration (s)'] = round(time.time() - start_time, 2)
            return result, list(set(new_urls))

    def _save_results(self, batch: List[Dict]):
        """Save a batch of results to CSV"""
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(batch[0].keys()))
            writer.writerows(batch)
        logging.info(f"Saved batch of {len(batch)} results")

    async def crawl(self):
        """Main crawl method"""
        self.start_time = time.time()
        logging.info(f"Starting crawl of {self.base_url}")

        async with aiohttp.ClientSession() as session:
            self.queue = [self.base_url]
            self.visited.add(self.base_url)
            self.all_urls.add(self.base_url)
            batch = []

            while self.queue:
                # Check timeout
                if (time.time() - self.start_time) > (self.timeout_minutes * 60):
                    logging.warning(f"Crawl timeout after {self.timeout_minutes} minutes")
                    break

                # Process URLs in larger batches
                current_batch = self.queue[:self.batch_size]
                self.queue = self.queue[self.batch_size:]

                # Process batch concurrently
                tasks = [self.process_url(session, url) for url in current_batch]
                results = await asyncio.gather(*tasks)

                for result, new_urls in results:
                    batch.append(result)
                    # Add new URLs to queue if not visited
                    for url in new_urls:
                        if url not in self.visited:
                            self.queue.append(url)
                            self.visited.add(url)

                # Save batch when it reaches batch_size
                if len(batch) >= self.batch_size:
                    self._save_results(batch)
                    batch = []

                # Log progress with metrics
                self._log_progress()

            # Save any remaining results
            if batch:
                self._save_results(batch)

            duration = time.time() - self.start_time
            success_rate = ((self.total_requests - self.failed_requests) / self.total_requests) * 100 if self.total_requests > 0 else 0
            avg_time_per_url = duration / len(self.visited) if len(self.visited) > 0 else 0

            logging.info(f"""Crawl completed:
            - Total time: {duration:.1f} seconds
            - Average time per URL: {avg_time_per_url:.2f} seconds
            - URLs crawled: {len(self.visited):,}
            - Successful requests: {self.total_requests - self.failed_requests:,}
            - Failed requests: {self.failed_requests:,}
            - Success rate: {success_rate:.1f}%
            - Final memory usage: {self._get_memory_usage()}""")

def main():
    """Entry point for the crawler"""
    if len(sys.argv) != 2:
        print("Usage: python crawler.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    crawler = WebCrawler(base_url, timeout_minutes=60)
    asyncio.run(crawler.crawl())

if __name__ == "__main__":
    main()