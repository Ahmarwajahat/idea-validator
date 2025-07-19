import os
from dotenv import load_dotenv
import logging
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_config(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("Gemini API key is required")
        if not cls.SERPAPI_API_KEY:
            logging.warning("SerpAPI key not found - competitor analysis will be limited")