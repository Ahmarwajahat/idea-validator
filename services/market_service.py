import requests
from config import Config
from urllib.parse import quote
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

def find_competitors(idea, industry=None):
    try:
        query = f"{idea} {industry or ''} startup competitor OR alternative OR similar"
        params = {
            'q': query,
            'api_key': Config.SERPAPI_API_KEY,
            'num': 5,  # Increased from 3 to 5
            'hl': 'en',
            'gl': 'us'
        }
        
        response = requests.get(
            'https://serpapi.com/search',
            params=params,
            timeout=15  # Increased timeout
        )
        response.raise_for_status()
        
        competitors = []
        seen_urls = set()
        
        for result in response.json().get('organic_results', [])[:5]:
            url = result.get('link', '#')
            if url not in seen_urls:
                competitors.append({
                    'name': clean_name(result.get('title', 'Unknown')),
                    'url': url,
                    'snippet': result.get('snippet', '')
                })
                seen_urls.add(url)
        
        return competitors
        
    except Exception as e:
        logger.error(f"Market Service Error: {str(e)}", exc_info=True)
        return [
            {"name": "Example Competitor 1", "url": "https://example.com", "snippet": "Sample competitor description"},
            {"name": "Example Competitor 2", "url": "https://example.com", "snippet": "Sample competitor description"}
        ]

def clean_name(name):
    if not name:
        return "Unknown"
    return name.split(' - ')[0].split(' | ')[0].split(' › ')[0].split('...')[0][:100]