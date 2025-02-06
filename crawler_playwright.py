from playwright.sync_api import sync_playwright
import requests
from urllib.parse import urlparse, urljoin
import csv
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables
visited_urls = set()
broken_links = {}
script_errors = {}
responsiveness_issues = {}
internal_domain = 'softwarefinder.com'

def is_internal(url):
    """Check if URL belongs to the target domain."""
    parsed = urlparse(url)
    if not parsed.netloc:
        return False
    return parsed.netloc.endswith(internal_domain) or \
           parsed.netloc.replace('www.', '') == internal_domain

def check_link_status(url):
    """Check the HTTP status of a URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    try:
        with requests.Session() as session:
            response = session.head(
                url,
                headers=headers,
                allow_redirects=True,
                timeout=15,
                verify=False  # Disable SSL verification for testing
            )
            if response.status_code in [405, 429]:  # Fallback to GET if HEAD fails
                response = session.get(url, headers=headers, timeout=15, verify=False)
            return response.status_code
    except Exception as e:
        return str(e)

def process_links(links, current_url, queue):
    """Process and validate links."""
    for link in set(links):
        if not link.startswith(('http://', 'https://')):
            link = urljoin(current_url, link)  # Handle relative URLs
        parsed = urlparse(link)
        if parsed.scheme in ('mailto', 'tel'):
            continue  # Skip non-HTTP links
        if is_internal(link) and link not in visited_urls and link not in queue:
            queue.append(link)  # Add new internal links to the queue

def check_responsiveness(page, current_url):
    """Check for responsiveness issues."""
    issues = []
    original_size = page.viewport_size
    
    # Test multiple viewports
    viewports = [
        {'name': 'mobile', 'width': 375, 'height': 667},
        {'name': 'tablet', 'width': 768, 'height': 1024},
        {'name': 'desktop', 'width': 1440, 'height': 900}
    ]
    
    for viewport in viewports:
        page.set_viewport_size(viewport)
        issues.extend(detect_layout_issues(page, viewport['name']))
    
    page.set_viewport_size(original_size)
    
    # Check for viewport meta tag
    if not page.query_selector('meta[name="viewport"]'):
        issues.append("Missing viewport meta tag")
    
    responsiveness_issues[current_url] = issues

def detect_layout_issues(page, viewport_name):
    """Detect layout issues for a given viewport."""
    return page.evaluate(f'''() => {{
        const issues = [];
        document.querySelectorAll('*').forEach(el => {{
            const rect = el.getBoundingClientRect();
            const overflowX = rect.right > window.innerWidth;
            const overflowY = rect.bottom > window.innerHeight;
            if (overflowX || overflowY) {{
                issues.push(`{viewport_name} viewport: ${{el.tagName}} overflow`);
            }}
        }});
        return issues;
    }}''')

def save_results_to_csv():
    """Save results to a CSV file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('crawl_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Page URL', 'Broken Links', 'Script Errors', 'Responsiveness Issues', 'Timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for url in visited_urls:
            writer.writerow({
                'Page URL': url,
                'Broken Links': '; '.join(broken_links.get(url, [])),
                'Script Errors': '; '.join(script_errors.get(url, [])),
                'Responsiveness Issues': '; '.join(responsiveness_issues.get(url, [])),
                'Timestamp': timestamp
            })

def crawl(start_url):
    """Crawl the website starting from the given URL."""
    with sync_playwright() as p:
        # Configure browser
        browser = p.chromium.launch(
            headless=True,
            timeout=120000,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        queue = [start_url]
        
        try:
            while queue:
                current_url = queue.pop(0)
                if current_url in visited_urls:
                    continue
                visited_urls.add(current_url)
                print(f"Crawling: {current_url}")

                broken_links[current_url] = []
                script_errors[current_url] = []
                page = context.new_page()
                
                try:
                    # Load the page
                    page.goto(current_url, wait_until='domcontentloaded', timeout=60000)
                    page.wait_for_load_state('networkidle', timeout=30000)
                    
                    # Capture JavaScript errors
                    page.on('console', lambda msg: (
                        script_errors[current_url].append(msg.text)
                        if msg.type == 'error' else None
                    ))
                    
                    # Check responsiveness
                    check_responsiveness(page, current_url)
                    
                    # Extract and process links
                    links = page.eval_on_selector_all(
                        'a', 'elements => elements.map(e => e.href)'
                    )
                    process_links(links, current_url, queue)
                    
                except Exception as e:
                    print(f"  Error processing {current_url}: {str(e)[:80]}")
                finally:
                    page.close()
        
        finally:
            # Cleanup and save results
            browser.close()
            save_results_to_csv()
            print(f"Crawl completed. Saved {len(visited_urls)} pages to crawl_results.csv")

if __name__ == '__main__':
    initial_url = 'https://softwarefinder.com'
    crawl(initial_url)