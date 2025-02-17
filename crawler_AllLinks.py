import asyncio
import csv
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import aiohttp

class AdvancedCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.queue = []
        self.results = []
        self.csv_file = 'crawl_report.csv'
        self._init_csv()
        self.session = None
        self.playwright = None
        self.browser = None
        self.semaphore = asyncio.Semaphore(10)
        self.devices = [
            {"name": "Mobile", "viewport": {"width": 375, "height": 667}},
            {"name": "Tablet", "viewport": {"width": 768, "height": 1024}},
            {"name": "Desktop", "viewport": {"width": 1366, "height": 768}}
        ]

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
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()
        await self.session.close()

    async def check_image(self, url):
        try:
            async with self.session.head(url) as response:
                if response.status >= 400:
                    return 'Broken', response.status
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
        if not soup.find('meta', attrs={'name': 'description'}):
            issues.append("Missing meta description")
        if len(soup.find_all('h1')) != 1:
            issues.append("Multiple H1 tags")
        return issues

    async def check_responsiveness(self, page, device):
        try:
            await page.set_viewport_size(device["viewport"])
            layout_issues = []
            elements = await page.query_selector_all('body *')
            for element in elements:
                box = await element.bounding_box()
                if box['width'] > device["viewport"]["width"]:
                    layout_issues.append("Content overflow")
                    break
            return layout_issues
        except:
            return []

    async def process_url(self, url, context):
        async with self.semaphore:
            entry = {
                'Url': url,
                'status code': None,
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

            try:
                page = await context.new_page()
                js_errors = []
                mixed_content = []
                responsiveness_issues = []

                # Event listeners
                page.on('console', lambda msg: js_errors.append(msg.text) if msg.type == 'error' else None)
                page.on('response', lambda response: mixed_content.append(response.url) 
                    if urlparse(url).scheme == 'https' and urlparse(response.url).scheme == 'http' else None)

                response = await page.goto(url, timeout=60000)
                entry['status code'] = response.status if response else 'N/A'

                # Wait for network idle
                await page.wait_for_load_state('networkidle')

                # Collect data
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # SEO analysis
                seo_issues = await self.analyze_seo(soup)
                if seo_issues:
                    entry['Seo issues'] = '; '.join(seo_issues)

                # Image analysis
                images = [urljoin(url, img['src']) for img in soup.find_all('img', src=True)]
                broken_images = []
                for img_url in images[:5]:  # Check first 5 images
                    error, detail = await self.check_image(img_url)
                    if error:
                        broken_images.append(f"{error}: {detail}")
                if broken_images:
                    entry['Broken images'] = '; '.join(broken_images)

                # Alt tags
                missing_alt = [urljoin(url, img['src']) for img in soup.find_all('img') if not img.get('alt')]
                if missing_alt:
                    entry['alt tags'] = f"Missing alt: {len(missing_alt)} images"

                # Meta tags
                meta_tags = {}
                for meta in soup.find_all('meta'):
                    name = meta.get('name', meta.get('property', 'unknown'))
                    meta_tags[name] = meta.get('content', '')
                entry['meta tags'] = str(meta_tags)[:500]

                # Responsiveness check
                device_issues = {}
                for device in self.devices:
                    await page.set_viewport_size(device["viewport"])
                    issues = await self.check_responsiveness(page, device)
                    if issues:
                        device_issues[device["name"]] = issues
                if device_issues:
                    entry['responsiveness issues'] = str(device_issues)
                    entry['device type'] = ', '.join(device_issues.keys())

                # CTA links
                cta_links = []
                for a in soup.find_all('a', href=True):
                    if 'cta' in a.get('class', []) or 'button' in a.get('class', []):
                        cta_links.append(urljoin(url, a['href']))
                if cta_links:
                    entry['CTA Internal links'] = '; '.join(cta_links[:5])

                # Heading structure
                headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1,7)}
                entry['heading tags'] = str(headings)

                # Finalize entries
                if js_errors:
                    entry['Js error'] = '; '.join(js_errors)[:500]
                if mixed_content:
                    entry['warnings'] = f"Mixed content: {len(mixed_content)} items"

                await page.close()
            except Exception as e:
                entry['notices'] = str(e)[:200]
            
            self.results.append(entry)
            if len(self.results) >= 10:
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
        context = await self.browser.new_context(ignore_https_errors=True)
        self.queue.append(self.base_url)
        self.visited.add(self.base_url)

        while self.queue:
            current_url = self.queue.pop(0)
            await self.process_url(current_url, context)
            links = await self.get_links(current_url, context)
            for link in links:
                if link not in self.visited:
                    self.visited.add(link)
                    self.queue.append(link)

        await self.save_results()
        await self.close()

    async def get_links(self, url, context):
        try:
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            links = await page.eval_on_selector_all('a[href]', 'elements => elements.map(e => e.href)')
            await page.close()
            return [link for link in links if urlparse(link).netloc == urlparse(self.base_url).netloc]
        except:
            return []

if __name__ == '__main__':
    crawler = AdvancedCrawler('https://softwarefinder.com')
    asyncio.run(crawler.start_crawl())