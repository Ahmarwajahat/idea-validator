from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from services.validator import validate_idea
from config import Config
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import traceback

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/analyze_idea": {
        "origins": ["*"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Ensure reports directory exists
os.makedirs('static/reports', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/analyze_idea', methods=['POST'])
def analyze_idea():
    logger.info("Received analyze_idea request")
    
    if not request.is_json:
        logger.error("Request must be JSON")
        return jsonify({
            'error': 'Invalid request format',
            'message': 'Request must be in JSON format'
        }), 400
    
    try:
        data = request.get_json()
        logger.debug(f"Request data: {data}")
        
        idea = data.get('idea', '').strip()
        industry = data.get('industry', '').strip() or None
        
        # Validate input
        if not idea:
            logger.error("No idea provided")
            return jsonify({
                'error': 'Validation error',
                'message': 'Please describe your startup idea',
                'code': 'MISSING_IDEA'
            }), 400
        
        if len(idea) < 20:
            logger.error(f"Idea too short ({len(idea)} chars)")
            return jsonify({
                'error': 'Validation error',
                'message': 'Description must be at least 20 characters long',
                'code': 'IDEA_TOO_SHORT',
                'min_length': 20,
                'current_length': len(idea)
            }), 400
        
        # Perform validation
        logger.info(f"Validating idea: {idea[:50]}...")
        validation_result = validate_idea(idea, industry)
        logger.info("Validation completed successfully")
        
        return jsonify({
            'status': 'success',
            'data': validation_result
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': 'Analysis failed',
            'message': 'An error occurred while analyzing your idea',
            'details': str(e),
            'code': 'ANALYSIS_ERROR'
        }), 500

@app.route('/static/reports/<filename>')
def serve_report(filename):
    return send_from_directory('static/reports', filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Server error: {str(e)}\n{traceback.format_exc()}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    Config.validate_config()
    app.run(host='0.0.0.0', port=5000, debug=True)