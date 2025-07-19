import google.generativeai as genai
from config import Config
import json
import re
import logging
import time
from functools import lru_cache
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Gemini with rate limiting
genai.configure(api_key=Config.GEMINI_API_KEY)
MODEL_NAME = 'gemini-1.0-pro'  # Using a more efficient model

@lru_cache(maxsize=100)
def get_cached_response(prompt):
    """Cache responses to reduce API calls"""
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    return generate_ai_response(prompt)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry_error_callback=lambda retry_state: None
)
def generate_ai_response(prompt, model_name=MODEL_NAME):
    """Generate AI response with rate limiting and retries"""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1000,  # Reduced from 2000
            },
            safety_settings={
                "HARASSMENT": "block_none",
                "HATE_SPEECH": "block_none",
                "SEXUAL": "block_none",
                "DANGEROUS": "block_none"
            }
        )
        time.sleep(1)  # Rate limiting
        return response.text
    except Exception as e:
        logger.error(f"AI Service Error: {str(e)}", exc_info=True)
        return None

def extract_json_from_response(response_text):
    """Extract JSON from AI response with robust error handling"""
    try:
        # Clean the response text first
        cleaned_text = response_text.strip()
        
        # Try direct parse first
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            pass
        
        # Try extracting JSON from markdown
        json_match = re.search(r'```(?:json)?\n?(.+?)\n?```', cleaned_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # Try extracting any JSON structure
        json_match = re.search(r'\{[\s\S]*\}', cleaned_text) or re.search(r'\[[\s\S]*\]', cleaned_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                pass
        
        # If all else fails, try to fix common JSON issues
        try:
            fixed_text = cleaned_text.replace('```json', '').replace('```', '')
            return json.loads(fixed_text)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from response")
            return None
    except Exception as e:
        logger.error(f"Error extracting JSON: {str(e)}", exc_info=True)
        return None