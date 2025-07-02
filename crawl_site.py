import json
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from utils import is_valid_url, is_internal_url, clean_url, load_robots_txt

with open("config.json", "r") as f:
    config = json.load(f)

START_URL = config["start_url"]
BASE_NETLOC = urlparse(START_URL).netloc
THROTTLE = config["throttle_seconds"]
MAX_PAGES = config["max_pages"]
RESPECT_ROBOTS = config["respect_robots_txt"]

OUTPUT_FILE = r"D:\internship\Better Analytics\chatbot\crawler\scraped_data.json"

visited = set()
results = []

# Helper to extract all visible text
def extract_visible_text(soup):
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    return ' '.join(soup.stripped_strings)[:5000]

def crawl_with_navigation(start_url):
    count = 0
    rp = load_robots_txt(start_url) if RESPECT_ROBOTS else None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(start_url, timeout=15000)
        page.wait_for_load_state("load")
        time.sleep(2)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        # Scrape homepage
        text = extract_visible_text(soup)
        results.append({"url": start_url, "question": f"What information is available on {start_url}?", "answer": text})
        visited.add(start_url)
        count += 1
        # Find all internal links on homepage
        links = []
        for tag in soup.find_all("a", href=True):
            full_url = urljoin(start_url, tag['href'])
            if is_valid_url(full_url) and is_internal_url(full_url, BASE_NETLOC):
                clean = clean_url(full_url)
                if clean not in visited and (not rp or rp.can_fetch("*", clean)):
                    links.append((clean, tag['href']))
        # Visit each link by clicking
        for clean, href in links:
            if count >= MAX_PAGES:
                break
            try:
                page.goto(start_url, timeout=15000)
                page.wait_for_load_state("load")
                time.sleep(1)
                page.click(f'a[href="{href}"]', timeout=5000)
                page.wait_for_load_state("load")
                time.sleep(2)
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                text = extract_visible_text(soup)
                results.append({"url": clean, "question": f"What information is available on {clean}?", "answer": text})
                visited.add(clean)
                count += 1
                time.sleep(THROTTLE)
            except Exception as e:
                print(f"[Error clicking {href}]: {e}")
        browser.close()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[Done] Scraped {len(results)} pages.")

if __name__ == "__main__":
    crawl_with_navigation(START_URL)