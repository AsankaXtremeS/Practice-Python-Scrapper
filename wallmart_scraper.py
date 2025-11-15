from bs4 import BeautifulSoup
import requests
import sys
import io
import json
import time
from requests.exceptions import ProxyError, HTTPError
import os
import urllib.parse

# Optional dotenv support; if python-dotenv is not installed, continue without it.
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return None

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# Configuration
BASE_URL = "https://www.walmart.com"
OUTPUT_FILE = "product_info.jsonl"

HEADERS = {
    # Use realistic browser headers to reduce bot detection (HTTP 412)
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not:A-Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "referer": "https://www.walmart.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}

# Proxy configuration (optional)
USE_PROXY = False
if USE_PROXY:
    host = 'brd.superproxy.io'
    port = 22225
    username = os.environ.get('BRD_USERNAME')
    password = os.environ.get('BRD_PASSWORD')
    # If credentials are missing, avoid KeyError and disable proxy gracefully
    if not username or not password:
        print("Proxy credentials not set in environment (BRD_USERNAME/BRD_PASSWORD). Disabling proxy.")
        PROXIES = None
    else:
        proxy_url = f'http://{username}:{password}@{host}:{port}'
        PROXIES = {'http': proxy_url, 'https': proxy_url}
else:
    PROXIES = None

# Use a persistent session so cookies and other headers are reused across requests.
session = requests.Session()
session.headers.update(HEADERS)
if PROXIES:
    session.proxies.update(PROXIES)

# Search queries
SEARCH_QUERIES = ["computers", "laptops", "desktops", "monitors", "printers"]

def extract_product_info(product_url):
    """Extract product information from a Walmart product page."""
    max_retries = 5
    backoff_factor = 3
    
    for attempt in range(max_retries):
        try:
            response = session.get(product_url, timeout=10)
            # If the server returns 412 (bot detection), save a debug snapshot and exit gracefully
            if response.status_code == 412:
                return None
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            script_tag = soup.find("script", id="__NEXT_DATA__")
            
            if not script_tag or not script_tag.string:
                return None
            
            data = json.loads(script_tag.string)
            initial_data = data.get("props", {}).get("pageProps", {}).get("initialData", {}).get("data", {})
            product_data = initial_data.get("product", {})
            reviews_data = initial_data.get("reviews", {}) or {}
            
            product_info = {
                "price": (product_data.get("priceInfo") or {}).get("currentPrice", {}).get("price"),
                "review_count": reviews_data.get("totalReviewCount", 0),
                "item_id": product_data.get("usItemId") or product_data.get("productId"),
                "avg_rating": reviews_data.get("averageOverallRating", 0),
                "product_name": product_data.get("name"),
                "brand": product_data.get("brand", ""),
                "availability": product_data.get("availabilityStatus"),
                "image_url": (product_data.get("imageInfo") or {}).get("thumbnailUrl"),
                "short_description": product_data.get("shortDescription", "")
            }
            
            return product_info
        
        except ProxyError as e:
            wait_time = backoff_factor ** attempt
            time.sleep(wait_time)
        except HTTPError as e:
            if e.response.status_code == 412:
                return None
            wait_time = backoff_factor ** attempt
            time.sleep(wait_time)
        except json.JSONDecodeError as e:
            return None
        except Exception as e:
            return None
    
    return None

def get_product_links_from_search_page(query, page_number):
    """Get product links from a Walmart search results page."""
    search_url = f"https://www.walmart.com/search?q={query}&page={page_number}"
    max_retries = 5
    backoff_factor = 3
    
    for attempt in range(max_retries):
        try:
            response = session.get(search_url, timeout=10)
            if response.status_code == 412:
                return []
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            product_links = []
            seen = set()

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # If it's a tracking redirect (sp/track), try to extract the real URL from the 'rd' query param
                if href.startswith('/sp/track') or '/sp/track' in href:
                    parsed = urllib.parse.urlparse(href)
                    qs = urllib.parse.parse_qs(parsed.query)
                    rd_vals = qs.get('rd') or qs.get('rd')
                    if rd_vals:
                        real = urllib.parse.unquote(rd_vals[0])
                        if "/ip/" in real:
                            full_url = real if real.startswith('http') else BASE_URL + real
                        else:
                            continue
                    else:
                        continue
                else:
                    # Accept only direct product paths or links that include /ip/
                    if '/ip/' not in href:
                        continue
                    full_url = href if href.startswith('http') else BASE_URL + href

                if full_url not in seen:
                    seen.add(full_url)
                    product_links.append(full_url)

            return product_links
        
        except ProxyError as e:
            wait_time = backoff_factor ** attempt
            time.sleep(wait_time)
        except HTTPError as e:
            if e.response.status_code == 412:
                return []
            wait_time = backoff_factor ** attempt
            time.sleep(wait_time)
        except Exception as e:
            return []
    
    return []

def main():
    """Main scraper function."""
    print(f"Starting Walmart product scraper...")
    print(f"Output file: {OUTPUT_FILE}\n")
    
    seen_urls = set()
    total_products = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        for query in SEARCH_QUERIES:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"{'='*60}")
            
            page_number = 1
            while page_number <= 2:  # Limit to first 2 pages per query
                product_links = get_product_links_from_search_page(query, page_number)
                
                if not product_links:
                    break
                
                for link in product_links:
                    if link not in seen_urls:
                        seen_urls.add(link)
                        product_info = extract_product_info(link)
                        
                        if product_info:
                            file.write(json.dumps(product_info, ensure_ascii=False) + "\n")
                            total_products += 1
                        
                        time.sleep(0.5)  # Be respectful to the server
                
                page_number += 1
    
    print(f"\n{'='*60}")
    print(f"Scraping completed!")
    print(f"Total products saved: {total_products}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()