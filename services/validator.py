from services.ai_service import generate_ai_response, extract_json_from_response, get_cached_response
from services.market_service import find_competitors
from services.pdf_service import generate_pdf_report
import json
import re
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

def validate_idea(idea, industry=None):
    """Validate a startup idea with comprehensive analysis"""
    try:
        # Validate input
        if not idea or len(idea.strip()) < 20:
            raise ValueError("Idea description must be at least 20 characters long")
            
        # Generate AI responses for different aspects
        prompts = {
            'feasibility': create_feasibility_prompt(idea, industry),
            'risks': create_risks_prompt(idea, industry),
            'improvements': create_improvements_prompt(idea, industry),
            'monetization': create_monetization_prompt(idea, industry),
            'investment': create_investment_prompt(idea, industry),
            'canvas': create_canvas_prompt(idea, industry),
            'market_size': create_market_size_prompt(idea, industry),
            'target_audience': create_target_audience_prompt(idea, industry)
        }
        
        # Process all prompts
        results = {}
        for key, prompt in prompts.items():
            fallback = globals().get(f"{key}_fallback", lambda: None)()
            results[key] = process_ai_response(prompt, fallback)
        
        # Find competitors
        competitors = find_competitors(idea, industry)
        
        # Calculate SWOT analysis
        swot_analysis = generate_swot_analysis(
            results.get('risks', []),
            results.get('improvements', []),
            results.get('monetization', []),
            idea,
            industry
        )
        
        # Generate PDF report
        pdf_report_path = generate_pdf_report({
            'idea': idea,
            'industry': industry,
            'analysis': {
                'feasibility_score': calculate_score(results.get('feasibility', {}).get('score', 7)),
                'swot_analysis': swot_analysis,
                'competitors': competitors,
                'monetization_paths': results.get('monetization', []),
                'improvements': results.get('improvements', [])
            }
        })
        
        # Prepare final result
        return {
            'feasibility_score': calculate_score(results.get('feasibility', {}).get('score', 7)),
            'feasibility_description': results.get('feasibility', {}).get('explanation', ''),
            'risks': results.get('risks', []),
            'improvements': results.get('improvements', []),
            'monetization_paths': results.get('monetization', []),
            'investment_needed': results.get('investment', {}),
            'competitors': competitors,
            'business_model_canvas': results.get('canvas', {}),
            'market_size': results.get('market_size', {}),
            'target_audience': results.get('target_audience', {}),
            'swot_analysis': swot_analysis,
            'analysis_date': datetime.now().isoformat(),
            'idea_summary': summarize_idea(idea),
            'success_probability': calculate_success_probability(
                results.get('feasibility', {}).get('score', 7),
                results.get('risks', []),
                len(competitors)
            ),
            'pdf_report_url': pdf_report_path
        }
    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        raise

# Prompt Creation Functions
def create_feasibility_prompt(idea, industry):
    return f"""Analyze this startup idea and provide a detailed feasibility assessment:
Idea: {idea}
Industry: {industry or 'Not specified'}

Consider:
1. Market demand and size
2. Technical feasibility
3. Competitive landscape
4. Business model viability
5. Potential challenges

Respond in this exact JSON format:
{{
    "score": <number between 1-10 where 10 is most feasible>,
    "explanation": "<detailed analysis (3-5 sentences)>"
}}"""

def create_risks_prompt(idea, industry):
    return f"""Identify specific, actionable risks for this startup idea:
Idea: {idea}
Industry: {industry or 'Not specified'}

Provide 3-5 risks as a JSON array, each risk should be:
- Specific to this idea
- Actionable (can be mitigated)
- Concise (1 sentence per risk)

Example: ["Market saturation in target industry", "High customer acquisition costs"]

Respond with just the JSON array:"""

def create_improvements_prompt(idea, industry):
    return f"""Suggest concrete improvements for this startup idea:
Idea: {idea}
Industry: {industry or 'Not specified'}

Provide 3-5 improvements as a JSON array, each should be:
- Actionable
- Specific
- Valuable

Example: ["Focus on a niche market first", "Develop strategic partnerships"]

Respond with just the JSON array:"""

def create_monetization_prompt(idea, industry):
    return f"""Suggest viable monetization strategies for this startup idea:
Idea: {idea}
Industry: {industry or 'Not specified'}

Provide 2-3 monetization paths as a JSON array, each should be:
- Realistic for this idea
- Include potential revenue models
- Consider industry standards

Example: ["Subscription SaaS model", "Freemium with premium features"]

Respond with just the JSON array:"""

def create_investment_prompt(idea, industry):
    return f"""Estimate the required investment for this startup idea:
Idea: {idea}
Industry: {industry or 'Not specified'}

Respond in this exact JSON format:
{{
    "amount": "<estimated dollar amount>",
    "level": "<low/moderate/high>",
    "break_even": "<estimated time to break even>",
    "cost_factors": ["<main cost factor 1>", "<main cost factor 2>"]
}}"""

def create_canvas_prompt(idea, industry):
    return f"""Create a complete business model canvas for this startup idea:
Idea: {idea}
Industry: {industry or 'Not specified'}

Respond in this exact JSON format:
{{
    "key_partners": ["partner1", "partner2"],
    "key_activities": ["activity1", "activity2"],
    "value_propositions": ["value1", "value2"],
    "customer_relationships": ["relationship1", "relationship2"],
    "customer_segments": ["segment1", "segment2"],
    "key_resources": ["resource1", "resource2"],
    "channels": ["channel1", "channel2"],
    "cost_structure": ["cost1", "cost2"],
    "revenue_streams": ["revenue1", "revenue2"]
}}"""

def create_market_size_prompt(idea, industry):
    return f"""Estimate the market size and growth potential for this startup idea:
Idea: {idea}
Industry: {industry or 'Not specified'}

Consider:
1. Total addressable market (TAM)
2. Serviceable available market (SAM)
3. Serviceable obtainable market (SOM)
4. Growth trends in the industry

Respond in this JSON format:
{{
    "tam": "<TAM estimate>",
    "sam": "<SAM estimate>",
    "som": "<SOM estimate>",
    "growth_rate": "<estimated annual growth rate>",
    "explanation": "<detailed analysis>"
}}"""

def create_target_audience_prompt(idea, industry):
    return f"""Identify the target audience for this startup idea:
Idea: {idea}
Industry: {industry or 'Not specified'}

Provide detailed information about:
1. Primary customer segments
2. Demographic characteristics
3. Psychographic characteristics
4. Buying behaviors

Respond in this JSON format:
{{
    "primary_segments": ["segment1", "segment2"],
    "demographics": {{
        "age_range": "<range>",
        "income_level": "<level>",
        "education": "<level>",
        "other": "<details>"
    }},
    "psychographics": {{
        "interests": ["interest1", "interest2"],
        "values": ["value1", "value2"],
        "lifestyle": "<description>"
    }},
    "buying_behaviors": {{
        "purchase_frequency": "<frequency>",
        "price_sensitivity": "<sensitivity>",
        "decision_factors": ["factor1", "factor2"]
    }}
}}"""

# Fallback Functions
def feasibility_fallback():
    return {'score': 7, 'explanation': 'Moderate potential based on limited information'}

def risks_fallback():
    return ['Market competition', 'Customer acquisition cost', 'Regulatory challenges']

def improvements_fallback():
    return ['Focus on niche market', 'Develop MVP quickly', 'Validate with early adopters']

def monetization_fallback():
    return ['Subscription model', 'Freemium with premium features', 'Enterprise licensing']

def investment_fallback():
    return {
        'amount': '50,000',
        'level': 'Moderate',
        'break_even': '12-18 months',
        'cost_factors': ['Development', 'Marketing', 'Staffing']
    }

def canvas_fallback():
    return {
        'key_partners': ['Technology providers', 'Marketing agencies'],
        'key_activities': ['Product development', 'Customer acquisition'],
        'value_propositions': ['Easy to use', 'Cost effective'],
        'customer_relationships': ['Self-service', 'Email support'],
        'customer_segments': ['Small businesses', 'Freelancers'],
        'key_resources': ['Development team', 'Brand'],
        'channels': ['Website', 'Social media'],
        'cost_structure': ['Fixed development costs', 'Variable marketing costs'],
        'revenue_streams': ['Subscriptions', 'Consulting']
    }

def market_size_fallback():
    return {
        'tam': '$10M',
        'sam': '$2M',
        'som': '$500K',
        'growth_rate': '15% annually',
        'explanation': 'Moderate market size with healthy growth potential'
    }

def target_audience_fallback():
    return {
        'primary_segments': ['Small businesses', 'Tech-savvy individuals'],
        'demographics': {
            'age_range': '25-45',
            'income_level': 'Middle to high',
            'education': 'College educated',
            'other': 'Urban dwellers'
        },
        'psychographics': {
            'interests': ['Technology', 'Productivity'],
            'values': ['Efficiency', 'Innovation'],
            'lifestyle': 'Busy professionals'
        },
        'buying_behaviors': {
            'purchase_frequency': 'Annual',
            'price_sensitivity': 'Moderate',
            'decision_factors': ['Features', 'Price']
        }
    }

# Helper Functions
def summarize_idea(idea: str) -> str:
    """Create a short summary of the idea"""
    if not idea:
        return ""
    clean_idea = ' '.join(idea.split()[:30])  # First 30 words
    return (clean_idea[:150] + '...') if len(clean_idea) > 150 else clean_idea

def process_ai_response(prompt, fallback):
    """Process AI response with proper error handling"""
    try:
        response = get_cached_response(prompt) or generate_ai_response(prompt)
        if response:
            json_data = extract_json_from_response(response)
            if json_data:
                return json_data
        logger.warning("Using fallback data for AI response")
        return fallback
    except Exception as e:
        logger.error(f"Error processing AI response: {str(e)}", exc_info=True)
        return fallback

def generate_swot_analysis(risks, improvements, monetization, idea, industry):
    prompt = f"""Generate a comprehensive SWOT analysis for this startup idea:
Idea: {idea}
Industry: {industry or 'Not specified'}

Consider these existing insights:
Risks: {risks}
Improvements: {improvements}
Monetization Paths: {monetization}

Provide a detailed SWOT analysis in this JSON format:
{{
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "opportunities": ["opportunity1", "opportunity2"],
    "threats": ["threat1", "threat2"]
}}"""
    
    fallback = {
        "strengths": ["Unique value proposition", "Growing market demand"],
        "weaknesses": ["High competition", "Customer acquisition cost"],
        "opportunities": ["Market expansion", "Strategic partnerships"],
        "threats": ["Regulatory changes", "Economic downturn"]
    }
    return process_ai_response(prompt, fallback)

def calculate_success_probability(score, risks, competitor_count):
    try:
        base_prob = score * 5  # Convert 1-10 score to 5-50%
        risk_factor = max(0, 1 - (len(risks) * 0.05))  # 5% reduction per risk
        competition_factor = max(0, 1 - (competitor_count * 0.02))  # 2% reduction per competitor
        return min(95, max(5, round(base_prob * risk_factor * competition_factor, 1)))
    except:
        return 50.0  # Default if calculation fails

def calculate_score(score):
    """Convert 1-10 score to 0-100 percentage with validation"""
    try:
        score = float(score)
        score = max(1, min(10, score))  # Clamp between 1-10
        return round(score * 10, 1)  # Convert to percentage
    except:
        logger.warning("Using default feasibility score")
        return 70.0  # Default score