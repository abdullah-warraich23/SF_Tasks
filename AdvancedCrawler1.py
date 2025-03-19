import asyncio
import csv
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Error as PlaywrightError

class WebCrawler:
    def __init__(self, base_url: str, output_file: str = "crawl_report_Adv.csv"):
        self.base_url = self._normalize_url(base_url)
        self.visited = set()  # Track visited URLs
        self.queue = []  # URL queue
        self.output_file = output_file
        self.results = []  # Store results before batch writing
        self._init_csv()
        
        # Device configurations for responsive testing
        self.devices = {
            "Mobile": {"width": 375, "height": 667},
            "Tablet": {"width": 768, "height": 1024},
            "Desktop": {"width": 1366, "height": 768}
        }

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to prevent duplicates"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc.lower()}"

    def _init_csv(self):
        """Initialize CSV file with headers"""
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'URL', 'Status Code', 'JS Error Type', 'HTTPS Status', 
                    'Load Time Issues', 'SEO Issues', 'Missing Alt Tags Count',
                    'Meta Description', 'Meta Keywords', 'Broken Images Count',
                    'Has CTA', 'H1 Count', 'H2 Count', 'H3 Count',
                    'Mobile Issues', 'Tablet Issues', 'Desktop Issues',
                    'Crawl Date', 'Crawl Time'
                ])

    async def _check_image(self, page, img_url: str) -> bool:
        """Check if image is broken"""
        try:
            response = await page.goto(img_url, wait_until='networkidle', timeout=5000)
            return response.status >= 400
        except PlaywrightError:
            return True
        finally:
            await page.goto('about:blank')  # Clear page

    def _summarize_js_error(self, error: str) -> str:
        """Convert JS errors into executive-friendly summaries"""
        error = error.lower()
        if 'connection' in error:
            return "Network Connection Error"
        elif 'timeout' in error:
            return "Page Load Timeout"
        elif 'syntax' in error:
            return "JavaScript Code Error"
        elif 'reference' in error:
            return "Missing Resource Error"
        return "Other JavaScript Error"

    async def _check_responsiveness(self, page, viewport: dict) -> str:
        """Test page responsiveness for a specific viewport"""
        await page.set_viewport_size(viewport)
        issues = await page.evaluate('''() => {
            const issues = [];
            document.querySelectorAll('*').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.right > window.innerWidth || rect.bottom > window.innerHeight) {
                    issues.push('Content overflow detected');
                }
            });
            return issues.join(', ') || 'No issues';
        }''')
        return issues

    def _analyze_seo(self, soup: BeautifulSoup) -> dict:
        """Analyze page for SEO issues"""
        h1s = soup.find_all('h1')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        
        issues = []
        if not h1s:
            issues.append("Missing H1")
        elif len(h1s) > 1:
            issues.append("Multiple H1 tags")
        if not meta_desc or not meta_desc.get('content', '').strip():
            issues.append("Missing meta description")
        if not meta_keywords or not meta_keywords.get('content', '').strip():
            issues.append("Missing meta keywords")
            
        return {
            'issues': '; '.join(issues) if issues else 'No SEO issues',
            'meta_description': meta_desc.get('content', '')[:500] if meta_desc else '',
            'meta_keywords': meta_keywords.get('content', '')[:500] if meta_keywords else ''
        }

    async def _process_url(self, browser: Browser, url: str) -> tuple[dict, list]:
        """Process a single URL and return its data and found links"""
        context = await browser.new_context()
        page = await context.new_page()
        
        result = {
            'URL': url,
            'Status Code': 0,
            'JS Error Type': 'None',
            'HTTPS Status': 'Secure' if url.startswith('https') else 'Not Secure',
            'Load Time Issues': 'None',
            'SEO Issues': '',
            'Missing Alt Tags Count': 0,
            'Meta Description': '',
            'Meta Keywords': '',
            'Broken Images Count': 0,
            'Has CTA': 'No',
            'H1 Count': 0,
            'H2 Count': 0,
            'H3 Count': 0,
            'Mobile Issues': '',
            'Tablet Issues': '',
            'Desktop Issues': '',
            'Crawl Date': datetime.now().strftime('%Y-%m-%d'),
            'Crawl Time': datetime.now().strftime('%H:%M:%S')
        }
        
        new_urls = []
        
        try:
            # Collect JS errors
            js_errors = []
            page.on('pageerror', lambda err: js_errors.append(err.message))
            
            # Load page with timeout
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            result['Status Code'] = response.status if response else 500
            
            # Wait for network idle with shorter timeout
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except PlaywrightError:
                result['Load Time Issues'] = 'Slow loading'
            
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Process JS errors
            if js_errors:
                result['JS Error Type'] = self._summarize_js_error(js_errors[0])
            
            # SEO Analysis
            seo_data = self._analyze_seo(soup)
            result.update({
                'SEO Issues': seo_data['issues'],
                'Meta Description': seo_data['meta_description'],
                'Meta Keywords': seo_data['meta_keywords']
            })
            
            # Image Analysis
            images = soup.find_all('img')
            result['Missing Alt Tags Count'] = len([img for img in images if not img.get('alt')])
            
            # Check for broken images
            img_urls = [urljoin(url, img['src']) for img in images if img.get('src')]
            broken_count = 0
            for img_url in img_urls[:10]:  # Limit to first 10 images for performance
                if await self._check_image(page, img_url):
                    broken_count += 1
            result['Broken Images Count'] = broken_count
            
            # CTA Check
            ctas = soup.find_all(['a', 'button'], class_=lambda x: x and ('cta' in x.lower() or 'button' in x.lower()))
            result['Has CTA'] = 'Yes' if ctas else 'No'
            
            # Heading Counts
            result['H1 Count'] = len(soup.find_all('h1'))
            result['H2 Count'] = len(soup.find_all('h2'))
            result['H3 Count'] = len(soup.find_all('h3'))
            
            # Responsive Testing
            for device, viewport in self.devices.items():
                issues = await self._check_responsiveness(page, viewport)
                result[f'{device} Issues'] = issues
            
            # Extract new URLs
            links = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(href => href && !href.startsWith('#') && !href.includes('mailto:'));
            }''')
            
            new_urls = [link for link in links if self._normalize_url(link) == self.base_url]
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            result['Load Time Issues'] = 'Failed to load'
        finally:
            await context.close()
        
        return result, list(set(new_urls))

    def _save_batch(self, batch: list):
        """Save a batch of results to CSV"""
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(batch[0].keys()))
            writer.writerows(batch)
        print(f"Saved batch of {len(batch)} results")

    async def crawl(self):
        """Main crawl method"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            self.queue = [self.base_url]
            self.visited.add(self.base_url)
            batch = []
            
            try:
                while self.queue:
                    # Process URLs in batches of 5
                    current_batch = self.queue[:5]
                    self.queue = self.queue[5:]
                    
                    # Process batch concurrently
                    tasks = [self._process_url(browser, url) for url in current_batch]
                    results = await asyncio.gather(*tasks)
                    
                    for result, new_urls in results:
                        batch.append(result)
                        # Add new URLs to queue if not visited
                        for url in new_urls:
                            if url not in self.visited:
                                self.queue.append(url)
                                self.visited.add(url)
                    
                    # Save batch when it reaches 20 results
                    if len(batch) >= 20:
                        self._save_batch(batch)
                        batch = []
                    
                    print(f"Processed {len(self.visited)} URLs, {len(self.queue)} remaining")
                
                # Save any remaining results
                if batch:
                    self._save_batch(batch)
                
            finally:
                await browser.close()
                print(f"Crawl completed. Processed {len(self.visited)} URLs")

def main():
    """Entry point for the crawler"""
    if len(sys.argv) != 2:
        print("Usage: python crawler.py <base_url>")
        sys.exit(1)
    
    base_url = sys.argv[1]
    crawler = WebCrawler(base_url)
    asyncio.run(crawler.crawl())

if __name__ == "__main__":
    import sys
    main()
