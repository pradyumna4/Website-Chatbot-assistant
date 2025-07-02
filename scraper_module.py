import requests
from bs4 import BeautifulSoup
import json
import os

DATA_FILE = r"D:\internship\Better Analytics\chatbot\raw data version\scraped_data.json"

def scrape_page(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = '\n'.join([p.get_text() for p in soup.find_all('p')])
        return text.strip()
    except Exception as e:
        return f"[Scraping Error] {str(e)}"

def load_scraped_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_scraped_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_url(url, force_refresh=False):
    data = load_scraped_data()
    if any(entry['url'] == url for entry in data) and not force_refresh:
        return f"[Info] URL already exists: {url}"

    content = scrape_page(url)
    if content.startswith("[Scraping Error]"):
        return content

    data.append({
        "url": url,
        "question": f"What information is available on {url}?",
        "answer": content[:2000]
    })

    save_scraped_data(data)
    return f"[Success] Scraped: {url}"