#!/usr/bin/env python3
"""
Debug Google Patents scraper - shows what elements are found
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def debug_google_search(inventor_name: str, assignee_name: str = None):
    """Debug what Google Patents returns"""
    
    # Build search URL
    query = f'inventor:"{inventor_name}"'
    if assignee_name:
        query += f' assignee:"{assignee_name}"'
    
    search_url = f"https://patents.google.com/?q={quote_plus(query)}"
    print(f"Searching: {search_url}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        response = session.get(search_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"\nPage title: {soup.title.string if soup.title else 'No title'}")
        
        # Check for different possible result containers
        selectors_to_try = [
            'search-result-item',
            'article',
            '.result',
            '[data-result]',
            '.search-result-item',
            'state-result',
            '.patent-result'
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            print(f"\nSelector '{selector}': Found {len(elements)} elements")
            
            if elements:
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    print(f"  Element {i+1}: {elem.name} with classes {elem.get('class', [])}")
                    text = elem.get_text(strip=True)[:200]
                    print(f"    Text preview: {text}...")
        
        # Look for any links that might be patent links
        patent_links = soup.find_all('a', href=True)
        patent_urls = []
        for link in patent_links:
            href = link['href']
            if 'patent/' in href and ('/US' in href or '/EP' in href):
                patent_urls.append(href)
        
        print(f"\nFound {len(patent_urls)} potential patent links:")
        for url in patent_urls[:5]:  # Show first 5
            print(f"  {url}")
        
        # Save page for manual inspection
        with open('debug_google_patents.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\nSaved page content to debug_google_patents.html")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_google_search("Ashok Raj", "Intel Corporation")