#!/usr/bin/env python3
"""
Test script to verify the CEWE photo book URL structure
"""

import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def test_url_structure():
    """Test the URL structure by checking a few pages"""
    base_url = "https://cewe.kruidvat.nl/web/42000005/photoBookPageRender.do?orderId=841684379&position=0&page=98&width=1080&hash=d19a90283ed4fd02254ff7710711be30&access=PY4EZ5"
    
    def build_page_url(page_number):
        """Build URL for a specific page number"""
        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)
        
        # Update the page parameter
        query_params['page'] = [str(page_number)]
        
        # Rebuild the URL
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                             parsed.params, new_query, parsed.fragment))
        return new_url
    
    # Test a few pages
    test_pages = [1, 2, 50, 98]
    
    print("Testing URL structure:")
    print(f"Base URL: {base_url}")
    print()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    for page in test_pages:
        url = build_page_url(page)
        print(f"Page {page}: {url}")
        
        try:
            response = session.head(url, timeout=10)  # Use HEAD to avoid downloading
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"  Content-Length: {response.headers.get('content-length', 'Unknown')}")
            
            if response.status_code == 200:
                print("  ✅ Success")
            else:
                print("  ❌ Failed")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error: {e}")
        
        print()


if __name__ == "__main__":
    test_url_structure() 