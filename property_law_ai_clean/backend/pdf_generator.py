from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, blue, red, green
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
import io
from datetime import datetime
from typing import Dict, Any
import logging

from models import User

logger = logging.getLogger(__name__)

class CaseReportPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2c3e50'),
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=HexColor('#3498db'),
            alignment=TA_LEFT
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#2c3e50'),
            alignment=TA_LEFT
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0
        ))
        
        # List item style
        self.styles.add(ParagraphStyle(
            name='ListItem',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10,
            alignment=TA_LEFT
        ))
        
        # Confidence score style
        self.styles.add(ParagraphStyle(
            name='ConfidenceScore',
            parent=self.styles['Normal'],
            fontSize=18,
            alignment=TA_CENTER,
            textColor=HexColor('#27ae60')
        ))

    def create_header(self, case_data: Dict[str, Any], user: User):
        """Create PDF header"""
        elements = []
        
        # Title
        title = Paragraph("Property Law AI Assistant", self.styles['CustomTitle'])
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph("Legal Case Analysis Report", self.styles['Subtitle'])
        elements.append(subtitle)
        
        # Case information table
        case_info = [
            ['Case Title:', case_data.get('title', 'N/A')],
            ['Dispute Type:', self.format_dispute_type(case_data.get('dispute_type', 'other'))],
            ['Analysis Date:', datetime.now().strftime('%B %d, %Y')],
            ['Generated For:', user.name],
            ['Case ID:', case_data.get('id', 'N/A')]
        ]
        
        case_table = Table(case_info, colWidths=[2*inch, 4*inch])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e1e8ed')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(Spacer(1, 20))
        elements.append(case_table)
        elements.append(Spacer(1, 30))
        
        return elements

    def create_confidence_section(self, ai_response: Dict[str, Any]):
        """Create confidence score section"""
        elements = []
        
        confidence_score = ai_response.get('confidence_score', 5)
        
        # Section heading
        heading = Paragraph("Confidence Assessment", self.styles['SectionHeading'])
        elements.append(heading)
        
        # Confidence score display
        score_color = self.get_confidence_color(confidence_score)
        score_text = f"<font color='{score_color}'>Confidence Score: {confidence_score}/10</font>"
        score_para = Paragraph(score_text, self.styles['ConfidenceScore'])
        elements.append(score_para)
        
        # Confidence explanation
        confidence_explanation = self.get_confidence_explanation(confidence_score)
        explanation_para = Paragraph(confidence_explanation, self.styles['BodyText'])
        elements.append(explanation_para)
        
        elements.append(Spacer(1, 20))
        return elements

    def create_case_summary_section(self, ai_response: Dict[str, Any]):
        """Create case summary section"""
        elements = []
        
        case_summary = ai_response.get('case_summary', {})
        
        # Section heading
        heading = Paragraph("Case Summary", self.styles['SectionHeading'])
        elements.append(heading)
        
        # Facts
        if case_summary.get('facts'):
            facts_heading = Paragraph("<b>Facts:</b>", self.styles['BodyText'])
            elements.append(facts_heading)
            facts_text = Paragraph(case_summary['facts'], self.styles['BodyText'])
            elements.append(facts_text)
            elements.append(Spacer(1, 10))
        
        # Claims
        if case_summary.get('claims'):
            claims_heading = Paragraph("<b>Claims:</b>", self.styles['BodyText'])
            elements.append(claims_heading)
            claims_text = Paragraph(case_summary['claims'], self.styles['BodyText'])
            elements.append(claims_text)
            elements.append(Spacer(1, 10))
        
        # Dispute Nature
        if case_summary.get('dispute_nature'):
            nature_heading = Paragraph("<b>Dispute Nature:</b>", self.styles['BodyText'])
            elements.append(nature_heading)
            nature_text = Paragraph(case_summary['dispute_nature'], self.styles['BodyText'])
            elements.append(nature_text)
        
        elements.append(Spacer(1, 20))
        return elements

    def create_legal_issues_section(self, ai_response: Dict[str, Any]):
        """Create legal issues section"""
        elements = []
        
        legal_issues = ai_response.get('legal_issues', [])
        
        if legal_issues:
            # Section heading
            heading = Paragraph("Key Legal Issues", self.styles['SectionHeading'])
            elements.append(heading)
            
            # List of issues
            for i, issue in enumerate(legal_issues, 1):
                issue_text = f"{i}. {issue}"
                issue_para = Paragraph(issue_text, self.styles['ListItem'])
                elements.append(issue_para)
            
            elements.append(Spacer(1, 20))
        
        return elements

    def create_applicable_laws_section(self, ai_response: Dict[str, Any]):
        """Create applicable laws section"""
        elements = []
        
        applicable_laws = ai_response.get('applicable_laws', [])
        
        if applicable_laws:
            # Section heading
            heading = Paragraph("Applicable Laws", self.styles['SectionHeading'])
            elements.append(heading)
            
            # Create table for laws
            law_data = [['Law/Section', 'Relevance']]
            for law in applicable_laws:
                law_data.append([
                    law.get('law', 'N/A'),
                    law.get('relevance', 'N/A')
                ])
            
            law_table = Table(law_data, colWidths=[2.5*inch, 3.5*inch])
            law_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#e1e8ed')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(law_table)
            elements.append(Spacer(1, 20))
        
        return elements

    def create_strategies_section(self, ai_response: Dict[str, Any]):
        """Create legal strategies section"""
        elements = []
        
        strategies = ai_response.get('strategies', {})
        
        if strategies:
            # Section heading
            heading = Paragraph("Legal Strategies", self.styles['SectionHeading'])
            elements.append(heading)
            
            # Plaintiff strategies
            plaintiff_strategies = strategies.get('plaintiff', [])
            if plaintiff_strategies:
                plaintiff_heading = Paragraph("<b>For Plaintiff:</b>", self.styles['BodyText'])
                elements.append(plaintiff_heading)
                
                for i, strategy in enumerate(plaintiff_strategies, 1):
                    strategy_text = f"{i}. {strategy}"
                    strategy_para = Paragraph(strategy_text, self.styles['ListItem'])
                    elements.append(strategy_para)
                
                elements.append(Spacer(1, 10))
            
            # Defendant strategies
            defendant_strategies = strategies.get('defendant', [])
            if defendant_strategies:
                defendant_heading = Paragraph("<b>For Defendant:</b>", self.styles['BodyText'])
                elements.append(defendant_heading)
                
                for i, strategy in enumerate(defendant_strategies, 1):
                    strategy_text = f"{i}. {strategy}"
                    strategy_para = Paragraph(strategy_text, self.styles['ListItem'])
                    elements.append(strategy_para)
            
            elements.append(Spacer(1, 20))
        
        return elements

    def create_next_steps_section(self, ai_response: Dict[str, Any]):
        """Create next steps section"""
        elements = []
        
        next_steps = ai_response.get('next_steps', [])
        
        if next_steps:
            # Section heading
            heading = Paragraph("Recommended Next Steps", self.styles['SectionHeading'])
            elements.append(heading)
            
            # List of steps
            for i, step in enumerate(next_steps, 1):
                step_text = f"{i}. {step}"
                step_para = Paragraph(step_text, self.styles['ListItem'])
                elements.append(step_para)
            
            elements.append(Spacer(1, 20))
        
        return elements

    def create_timeline_costs_section(self, ai_response: Dict[str, Any]):
        """Create timeline and costs section"""
        elements = []
        
        timeline = ai_response.get('estimated_timeline')
        costs = ai_response.get('estimated_costs')
        
        if timeline or costs:
            # Section heading
            heading = Paragraph("Timeline & Cost Estimates", self.styles['SectionHeading'])
            elements.append(heading)
            
            if timeline:
                timeline_heading = Paragraph("<b>Estimated Timeline:</b>", self.styles['BodyText'])
                elements.append(timeline_heading)
                timeline_text = Paragraph(timeline, self.styles['BodyText'])
                elements.append(timeline_text)
                elements.append(Spacer(1, 10))
            
            if costs:
                costs_heading = Paragraph("<b>Estimated Costs:</b>", self.styles['BodyText'])
                elements.append(costs_heading)
                costs_text = Paragraph(costs, self.styles['BodyText'])
                elements.append(costs_text)
            
            elements.append(Spacer(1, 20))
        
        return elements

    def create_footer(self):
        """Create PDF footer"""
        elements = []
        
        # Disclaimer
        disclaimer_text = """
        <b>IMPORTANT DISCLAIMER:</b><br/>
        This report is generated by an AI system for informational purposes only and should not be considered as legal advice. 
        The analysis is based on the information provided and general legal principles. For specific legal advice, 
        please consult with a qualified property lawyer in Bangalore who can review your case in detail and provide 
        personalized guidance based on current laws and regulations.
        """
        
        disclaimer = Paragraph(disclaimer_text, self.styles['BodyText'])
        elements.append(disclaimer)
        
        elements.append(Spacer(1, 20))
        
        # Generated by
        generated_text = f"Generated by Property Law AI Assistant on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        generated = Paragraph(generated_text, self.styles['Normal'])
        elements.append(generated)
        
        return elements

    def format_dispute_type(self, dispute_type: str) -> str:
        """Format dispute type for display"""
        type_mapping = {
            'inheritance': 'Inheritance & Partition',
            'boundary': 'Boundary Disputes',
            'mutation': 'Mutation & Title Issues',
            'tax': 'Property Tax Issues',
            'bbmp_bda': 'BBMP/BDA Issues',
            'other': 'Other Property Issues'
        }
        return type_mapping.get(dispute_type, dispute_type.title())

    def get_confidence_color(self, score: int) -> str:
        """Get color based on confidence score"""
        if score >= 7:
            return '#27ae60'  # Green
        elif score >= 4:
            return '#f39c12'  # Orange
        else:
            return '#e74c3c'  # Red

    def get_confidence_explanation(self, score: int) -> str:
        """Get explanation for confidence score"""
        if score >= 7:
            return "High confidence: The analysis is based on clear facts and straightforward legal application."
        elif score >= 4:
            return "Medium confidence: The analysis provides good guidance, but some key information may be missing."
        else:
            return "Low confidence: The analysis is preliminary due to insufficient facts or complex legal issues. Professional consultation is strongly recommended."

async def generate_case_report_pdf(case_data: Dict[str, Any], user: User) -> bytes:
    """Generate PDF report for a case"""
    try:
        logger.info(f"Generating PDF report for case: {case_data.get('id')}")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Create PDF generator instance
        pdf_generator = CaseReportPDF()
        
        # Build PDF content
        elements = []
        
        # Header
        elements.extend(pdf_generator.create_header(case_data, user))
        
        # AI Response sections
        ai_response = case_data.get('ai_response', {})
        
        # Confidence assessment
        elements.extend(pdf_generator.create_confidence_section(ai_response))
        
        # Case summary
        elements.extend(pdf_generator.create_case_summary_section(ai_response))
        
        # Legal issues
        elements.extend(pdf_generator.create_legal_issues_section(ai_response))
        
        # Applicable laws
        elements.extend(pdf_generator.create_applicable_laws_section(ai_response))
        
        # Legal strategies
        elements.extend(pdf_generator.create_strategies_section(ai_response))
        
        # Next steps
        elements.extend(pdf_generator.create_next_steps_section(ai_response))
        
        # Timeline and costs
        elements.extend(pdf_generator.create_timeline_costs_section(ai_response))
        
        # Page break before footer
        elements.append(PageBreak())
        
        # Footer
        elements.extend(pdf_generator.create_footer())
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"PDF report generated successfully for case: {case_data.get('id')}")
        
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise Exception(f"PDF generation failed: {str(e)}")