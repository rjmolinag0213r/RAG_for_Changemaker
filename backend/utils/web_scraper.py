
"""Web scraping utilities using BeautifulSoup."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
from backend.config import settings
from backend.utils.logger import log


class WebScraper:
    """Handle web scraping operations."""
    
    def __init__(self):
        """Initialize the web scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.scraping.user_agent
        })
        self.timeout = settings.scraping.timeout
        log.info("WebScraper initialized")
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped content and metadata
        """
        try:
            log.info(f"Scraping URL: {url}")
            
            # Fetch the page
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string.strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            
            # Extract main content
            # Try to find main content area
            main_content = None
            for tag in ['main', 'article', 'div[class*="content"]', 'div[id*="content"]']:
                main_content = soup.find(tag)
                if main_content:
                    break
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.find('body')
            
            # Extract text
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text (remove excessive whitespace)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n\n'.join(lines)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = urljoin(url, link['href'])
                links.append(href)
            
            result = {
                "url": url,
                "title": title,
                "text": text,
                "links": links,
                "status_code": response.status_code,
                "content_type": response.headers.get('Content-Type', ''),
            }
            
            log.info(f"Successfully scraped {url}: {len(text)} characters extracted")
            return result
            
        except requests.RequestException as e:
            log.error(f"Error scraping URL {url}: {e}")
            raise
        except Exception as e:
            log.error(f"Unexpected error scraping URL {url}: {e}")
            raise
    
    def extract_links(self, url: str, same_domain_only: bool = True) -> List[str]:
        """
        Extract all links from a URL.
        
        Args:
            url: URL to extract links from
            same_domain_only: Only return links from the same domain
            
        Returns:
            List of URLs
        """
        try:
            result = self.scrape_url(url)
            links = result['links']
            
            if same_domain_only:
                base_domain = urlparse(url).netloc
                links = [link for link in links if urlparse(link).netloc == base_domain]
            
            return list(set(links))  # Remove duplicates
            
        except Exception as e:
            log.error(f"Error extracting links from {url}: {e}")
            return []
    
    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of scraped content dictionaries
        """
        results = []
        for url in urls:
            try:
                result = self.scrape_url(url)
                results.append(result)
            except Exception as e:
                log.error(f"Failed to scrape {url}: {e}")
                continue
        
        return results
