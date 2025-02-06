"""
Data collection module with support for multiple sources
"""
import time
import logging
from typing import List, Dict, Optional
import requests
from tenacity import retry, wait_exponential, stop_after_attempt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """Handles data collection from multiple sources with rate limiting"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 'ResearchBot/1.0')
        })
        
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10),
           stop=stop_after_attempt(3))
    def collect_from_source(self, query: str, source: str) -> List[Dict]:
        """Collect data from a specific source with retry logic"""
        if source == 'google':
            return self._collect_from_google(query)
        elif source == 'arxiv':
            return self._collect_from_arxiv(query)
        else:
            raise ValueError(f"Unsupported source: {source}")

    def _collect_from_google(self, query: str) -> List[Dict]:
        """Collect data from Google Custom Search API"""
        endpoint = self.config['sources']['google']['endpoint']
        params = {
            'key': self.config['api_keys']['google'],
            'cx': self.config['sources']['google']['cx'],
            'q': query,
            'num': 10
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return [{
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': 'google'
            } for item in data.get('items', [])]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google API error: {str(e)}")
            return []

    def collect_data(self, query: str, sources: Optional[List[str]] = None) -> List[Dict]:
        """Collect data from all specified sources"""
        if sources is None:
            sources = ['google', 'arxiv']
            
        all_results = []
        for source in sources:
            try:
                results = self.collect_from_source(query, source)
                all_results.extend(results)
                time.sleep(self.config.get('rate_limit', 1))  # Rate limiting
            except Exception as e:
                logger.error(f"Error collecting from {source}: {str(e)}")
                
        return all_results 