from fpdf import FPDF
import os
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Startup Idea Validation Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(data, output_dir='static/reports'):
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create PDF
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add metadata
        pdf.cell(0, 10, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1)
        pdf.cell(0, 10, f"Idea: {data.get('idea', '')[:100]}", ln=1)
        pdf.cell(0, 10, f"Industry: {data.get('industry', 'Not specified')}", ln=1)
        pdf.ln(10)
        
        # Add analysis sections
        analysis = data.get('analysis', {})
        
        # Feasibility Score
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Feasibility Analysis', ln=1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Score: {analysis.get('feasibility_score', 0)}/100", ln=1)
        pdf.ln(5)
        
        # SWOT Analysis
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'SWOT Analysis', ln=1)
        pdf.set_font('Arial', '', 12)
        
        swot = analysis.get('swot_analysis', {})
        for category in ['strengths', 'weaknesses', 'opportunities', 'threats']:
            pdf.cell(0, 10, f"{category.capitalize()}:", ln=1)
            for item in swot.get(category, []):
                pdf.cell(10)  # Indent
                pdf.cell(0, 10, f"- {item}", ln=1)
            pdf.ln(3)
        
        # Competitors
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Competitor Analysis', ln=1)
        pdf.set_font('Arial', '', 12)
        for competitor in analysis.get('competitors', [])[:5]:  # Limit to top 5
            pdf.cell(0, 10, f"- {competitor.get('name', 'Unknown')}", ln=1)
            pdf.cell(10)
            pdf.multi_cell(0, 10, competitor.get('snippet', 'No description available'))
            pdf.ln(2)
        
        # Save file
        filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(output_dir, filename)
        pdf.output(filepath)
        
        return f"/static/reports/{filename}"  # Return web-accessible path
    except Exception as e:
        logger.error(f"PDF Generation Error: {str(e)}", exc_info=True)
        return None