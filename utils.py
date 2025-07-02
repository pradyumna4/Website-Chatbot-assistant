from urllib.parse import urlparse, urljoin
import re
import urllib.robotparser as robotparser

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)

def clean_url(url):
    return url.split('#')[0].split('?')[0].rstrip('/')

def is_internal_url(url, base_netloc):
    return urlparse(url).netloc == base_netloc

def load_robots_txt(start_url):
    rp = robotparser.RobotFileParser()
    parsed = urlparse(start_url)
    robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
    rp.set_url(robots_url)
    try:
        rp.read()
    except:
        pass
    return rp
