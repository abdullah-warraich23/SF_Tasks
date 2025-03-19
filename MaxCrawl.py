import asyncio
import csv
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import aiohttp

class UnlimitedCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.queue = []
        self.results = []
        self.csv_file = 'crawl_report2.csv'
        self._init_csv()
        self.session = None
        self.playwright = None
        self.browser = None
        self.context = None
        self.semaphore = asyncio.Semaphore(20)  # Increased concurrency
        self.devices = [
            {"name": "Mobile", "viewport": {"width": 375, "height": 667}},
            {"name": "Tablet", "viewport": {"width": 768, "height": 1024}},
            {"name": "Desktop", "viewport": {"width": 1366, "height": 768}}
        ]
        self.crawl_count = 0

    def _init_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Url', 'status code', 'Js error', 'warnings', 'notices',
                    'Seo issues', 'alt tags', 'meta tags', 'Broken images',
                    'CTA Internal links', 'heading tags', 'responsiveness issues',
                    'device type', 'date', 'time'
                ])

    async def setup(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            ignore_https_errors=True,
            java_script_enabled=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()
        await self.session.close()

    async def check_image(self, url):
        try:
            async with self.session.head(url) as response:
                status = response.status
                if status >= 400:
                    return 'Broken', status
                content_type = response.headers.get('Content-Type', '')
                if 'avif' not in content_type:
                    return 'Invalid format', content_type
                return None, None
        except Exception as e:
            return 'Error', str(e)

    async def analyze_seo(self, soup):
        issues = []
        if not soup.find('title'):
            issues.append("Missing title tag")
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content', '').strip():
            issues.append("Missing/invalid meta description")
        if len(soup.find_all('h1')) != 1:
            issues.append("Multiple H1 tags")
        return issues

    async def check_responsiveness(self, page, device):
        try:
            await page.set_viewport_size(device["viewport"])
            issues = await page.evaluate('''async () => {
                const elements = Array.from(document.body.getElementsByTagName('*'));
                const viewportWidth = window.innerWidth;
                const viewportHeight = window.innerHeight;
                const issues = [];
                
                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    if (rect.right > viewportWidth || rect.bottom > viewportHeight) {
                        issues.push(`${el.tagName} overflow detected`);
                    }
                    if (el.offsetWidth > viewportWidth) {
                        issues.push(`${el.tagName} width exceeds viewport`);
                    }
                }
                return issues;  // No limit on issues
            }''')
            return issues
        except:
            return []

    async def process_url(self, url):
        async with self.semaphore:
            self.crawl_count += 1
            print(f"Crawling #{self.crawl_count}: {url}")
            entry = {
                'Url': url,
                'status code': 0,
                'Js error': 'null',
                'warnings': 'null',
                'notices': 'null',
                'Seo issues': 'null',
                'alt tags': 'null',
                'meta tags': 'null',
                'Broken images': 'null',
                'CTA Internal links': 'null',
                'heading tags': 'null',
                'responsiveness issues': 'null',
                'device type': 'null',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S')
            }

            page = None
            try:
                page = await self.context.new_page()
                js_errors = []
                mixed_content = []
                responsiveness_issues = {}

                # Setup listeners first
                page.on('console', lambda msg: js_errors.append(msg.text) if msg.type == 'error' else None)
                page.on('response', lambda response: mixed_content.append(response.url) 
                    if urlparse(url).scheme == 'https' and urlparse(response.url).scheme == 'http' else None)

                # Navigate with timeout handling
                try:
                    response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    entry['status code'] = response.status if response else 0
                except Exception as e:
                    entry['notices'] = str(e)[:200]
                    entry['status code'] = 500  # Default error code

                # Collect content if page loaded
                if entry['status code'] < 400:
                    await page.wait_for_load_state('networkidle', timeout=15000)
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')

                    # SEO analysis
                    seo_issues = await self.analyze_seo(soup)
                    if seo_issues:
                        entry['Seo issues'] = '; '.join(seo_issues)

                    # Image analysis (parallel processing)
                    images = [urljoin(url, img['src']) for img in soup.find_all('img', src=True)]
                    image_tasks = [self.check_image(img_url) for img_url in images]  # Check ALL images
                    image_results = await asyncio.gather(*image_tasks)
                    broken_images = [f"{res[0]}: {res[1]}" for res in image_results if res[0]]
                    if broken_images:
                        entry['Broken images'] = '; '.join(broken_images)

                    # Alt tags
                    missing_alt = [urljoin(url, img['src']) for img in soup.find_all('img') if not img.get('alt')]
                    if missing_alt:
                        entry['alt tags'] = f"Missing alt: {len(missing_alt)} images"

                    # Meta tags
                    meta_tags = {meta.get('name', meta.get('property', 'unknown')): meta.get('content', '')
                                for meta in soup.find_all('meta')}
                    entry['meta tags'] = str(meta_tags)[:500]

                    # Responsiveness checks (parallel across devices)
                    device_tasks = [self.check_responsiveness(page, device) for device in self.devices]
                    device_results = await asyncio.gather(*device_tasks)
                    for device, issues in zip(self.devices, device_results):
                        if issues:
                            responsiveness_issues[device["name"]] = issues  # No limit on issues
                    if responsiveness_issues:
                        entry['responsiveness issues'] = str(responsiveness_issues)
                        entry['device type'] = ', '.join(responsiveness_issues.keys())

                    # CTA links
                    cta_links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)
                                if any(cls in ['cta', 'button'] for cls in a.get('class', []))]
                    if cta_links:
                        entry['CTA Internal links'] = '; '.join(cta_links)

                    # Heading structure
                    headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1,7)}
                    entry['heading tags'] = str(headings)

                # Finalize entries
                if js_errors:
                    entry['Js error'] = '; '.join(js_errors)
                if mixed_content:
                    entry['warnings'] = f"Mixed content: {len(mixed_content)} items"

            except Exception as e:
                entry['notices'] = str(e)[:200]
            finally:
                if page:
                    await page.close()
            
            self.results.append(entry)
            if len(self.results) >= 20:
                await self.save_results()

    async def save_results(self):
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Url', 'status code', 'Js error', 'warnings', 'notices',
                'Seo issues', 'alt tags', 'meta tags', 'Broken images',
                'CTA Internal links', 'heading tags', 'responsiveness issues',
                'device type', 'date', 'time'
            ])
            writer.writerows(self.results)
            self.results = []

    async def start_crawl(self):
        await self.setup()
        self.queue.append(self.base_url)
        self.visited.add(self.base_url)

        while self.queue:
            batch = self.queue[:50]  # Process in batches
            del self.queue[:50]
            tasks = [self.process_url(url) for url in batch]
            await asyncio.gather(*tasks)
            
            # Parallel link discovery
            link_tasks = [self.get_links(url) for url in batch]
            links = await asyncio.gather(*link_tasks)
            new_links = set()
            for link_group in links:
                new_links.update(link_group)
            new_links -= self.visited
            self.visited.update(new_links)
            self.queue.extend(new_links)

        await self.save_results()
        await self.close()

    async def get_links(self, url):
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'lxml')
                    return [urljoin(url, a['href']) for a in soup.find_all('a', href=True)
                           if urlparse(urljoin(url, a['href'])).netloc == urlparse(self.base_url).netloc]
                return []
        except:
            return []

if __name__ == '__main__':
    crawler = UnlimitedCrawler('https://softwarefinder.com')
    asyncio.run(crawler.start_crawl())