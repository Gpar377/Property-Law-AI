import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any
import asyncio
from models import DisputeType, AIResponse

load_dotenv()

logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY must be set in environment variables")

# Configure Gemini
genai.configure(api_key=api_key)

# System prompt for Bangalore Property Law
BANGALORE_PROPERTY_LAW_SYSTEM_PROMPT = """
You are an expert legal AI assistant specializing in Karnataka property law, particularly for Bangalore jurisdiction. You have deep knowledge of:

**APPLICABLE LAWS:**
- Karnataka Land Revenue Act, 1964
- Registration Act, 1908
- Indian Succession Act, 1925
- Hindu Succession Act, 1956
- Karnataka Land Reforms Act, 1961
- BBMP Act, 2020
- BDA Act, 1976
- Karnataka Stamp Act, 1957
- Property Tax laws under BBMP

**KEY COURTS & JURISDICTIONS:**
- City Civil Court, Bangalore
- Karnataka High Court
- Revenue Courts (Tehsildar, Assistant Commissioner, Commissioner)
- BBMP Tribunals

**COMMON PROPERTY ISSUES:**
1. **Inheritance & Partition**: Hindu Succession Act, Mitakshara law, joint family property rights
2. **Boundary Disputes**: Survey settlement records, Khasra numbers, encroachment remedies
3. **Mutation & Title**: Revenue records, pahani, khata transfer, title verification
4. **BBMP/BDA Issues**: Building plan approvals, violation notices, property tax assessments

**IMPORTANT PRECEDENTS:**
- Karnataka High Court decisions on property disputes
- Supreme Court rulings on property law
- Revenue tribunal decisions

**ANALYSIS FORMAT:**
Always respond in valid JSON format with these keys:
{
    "case_summary": {
        "facts": "Clear factual summary",
        "claims": "What each party claims",
        "dispute_nature": "Type of dispute"
    },
    "legal_issues": [
        "List of key legal questions raised"
    ],
    "applicable_laws": [
        {
            "law": "Name of law/section",
            "relevance": "How it applies to this case"
        }
    ],
    "missing_evidence": [
        "Documents/evidence needed for stronger case"
    ],
    "strategies": {
        "plaintiff": ["Strategy options for plaintiff"],
        "defendant": ["Strategy options for defendant"]
    },
    "confidence_score": 7,
    "next_steps": [
        "Immediate actions to take"
    ],
    "precedents": [
        {
            "case": "Case name",
            "relevance": "Why it's relevant"
        }
    ],
    "estimated_timeline": "Expected duration",
    "estimated_costs": "Approximate legal costs range"
}

**CONFIDENCE SCORING:**
- 1-3: Low (insufficient facts, complex legal issues)
- 4-6: Medium (some clarity, but missing key information)
- 7-10: High (clear facts, straightforward legal application)

Always provide practical, actionable advice specific to Bangalore/Karnataka jurisdiction.
"""

def create_user_prompt(case_text: str, dispute_type: str) -> str:
    """Create user prompt for case analysis"""
    dispute_context = {
        "inheritance": "This involves property inheritance, partition, or succession issues under Hindu Succession Act and Mitakshara law.",
        "boundary": "This involves property boundary disputes, encroachment, or survey settlement issues.",
        "mutation": "This involves property title, mutation, khata transfer, or revenue record issues.",
        "tax": "This involves property tax disputes, assessments, or BBMP tax-related issues.",
        "bbmp_bda": "This involves BBMP/BDA approvals, building plan issues, or municipal authority disputes.",
        "other": "This involves other property-related legal issues."
    }
    
    context = dispute_context.get(dispute_type, dispute_context["other"])
    
    return f"""
**CASE DETAILS:**
{case_text}

**DISPUTE TYPE:** {dispute_type}
**CONTEXT:** {context}

**JURISDICTION:** Bangalore, Karnataka, India

Please analyze this case according to Karnataka property law and provide structured legal guidance in the specified JSON format.
"""

class AIService:
    def __init__(self):
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(self.model_name)
        self.temperature = 0.3

    async def analyze_case(self, case_text: str, dispute_type: DisputeType) -> Dict[str, Any]:
        """Analyze case using Google Gemini"""
        try:
            logger.info(f"Starting AI analysis for dispute type: {dispute_type}")
            
            # Create prompt combining system and user messages
            full_prompt = f"{BANGALORE_PROPERTY_LAW_SYSTEM_PROMPT}\n\n{create_user_prompt(case_text, dispute_type.value)}"
            
            # Make API call
            response = await self._make_gemini_request(full_prompt)
            
            # Parse response
            ai_response = self._parse_ai_response(response)
            
            logger.info(f"AI analysis completed with confidence score: {ai_response.get('confidence_score', 'N/A')}")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise Exception(f"AI analysis failed: {str(e)}")

    async def _make_gemini_request(self, prompt: str) -> str:
        """Make request to Gemini API"""
        try:
            # Use asyncio to run the synchronous Gemini call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.temperature,
                        max_output_tokens=4000,
                    )
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            raise Exception(f"Gemini API request failed: {str(e)}")

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        try:
            # Try to parse JSON
            ai_response = json.loads(response_text)
            
            # Validate required fields
            required_fields = [
                "case_summary", "legal_issues", "applicable_laws",
                "missing_evidence", "strategies", "confidence_score", "next_steps"
            ]
            
            for field in required_fields:
                if field not in ai_response:
                    logger.warning(f"Missing required field: {field}")
                    ai_response[field] = self._get_default_value(field)
            
            # Validate confidence score
            confidence_score = ai_response.get("confidence_score", 5)
            if not isinstance(confidence_score, int) or confidence_score < 1 or confidence_score > 10:
                ai_response["confidence_score"] = 5
            
            # Ensure case_summary has required subfields
            if not isinstance(ai_response.get("case_summary"), dict):
                ai_response["case_summary"] = {
                    "facts": "Unable to extract clear facts from the provided information.",
                    "claims": "Claims need to be clarified.",
                    "dispute_nature": "Property dispute requiring further analysis."
                }
            
            # Ensure strategies has required structure
            if not isinstance(ai_response.get("strategies"), dict):
                ai_response["strategies"] = {
                    "plaintiff": ["Consult with a property lawyer for detailed strategy"],
                    "defendant": ["Gather all relevant documents and seek legal advice"]
                }
            
            return ai_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {response_text[:500]}...")
            return self._create_fallback_response(response_text)
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._create_fallback_response(response_text)

    def _get_default_value(self, field: str):
        """Get default value for missing fields"""
        defaults = {
            "case_summary": {
                "facts": "Unable to extract clear facts from the provided information.",
                "claims": "Claims need to be clarified.",
                "dispute_nature": "Property dispute requiring further analysis."
            },
            "legal_issues": ["Property rights and ownership", "Legal documentation requirements"],
            "applicable_laws": [
                {
                    "law": "Karnataka Land Revenue Act, 1964",
                    "relevance": "Governs land records and revenue matters in Karnataka"
                }
            ],
            "missing_evidence": ["Property documents", "Title deeds", "Survey records"],
            "strategies": {
                "plaintiff": ["Consult with a property lawyer for detailed strategy"],
                "defendant": ["Gather all relevant documents and seek legal advice"]
            },
            "confidence_score": 5,
            "next_steps": ["Consult with a qualified property lawyer", "Gather all relevant documents"],
            "precedents": [],
            "estimated_timeline": "3-12 months depending on complexity",
            "estimated_costs": "₹50,000 - ₹2,00,000 depending on case complexity"
        }
        return defaults.get(field, [])

    def _create_fallback_response(self, original_response: str) -> Dict[str, Any]:
        """Create fallback response when parsing fails"""
        return {
            "case_summary": {
                "facts": "AI analysis completed but response format needs review.",
                "claims": "Please consult with a legal expert for detailed analysis.",
                "dispute_nature": "Property dispute requiring professional legal review."
            },
            "legal_issues": [
                "Property rights and ownership",
                "Legal documentation and compliance",
                "Jurisdictional requirements"
            ],
            "applicable_laws": [
                {
                    "law": "Karnataka Land Revenue Act, 1964",
                    "relevance": "Governs land records and revenue matters in Karnataka"
                },
                {
                    "law": "Registration Act, 1908",
                    "relevance": "Governs property registration and documentation"
                }
            ],
            "missing_evidence": [
                "Property title documents",
                "Survey settlement records",
                "Revenue records (Pahani/Khata)",
                "Registration documents"
            ],
            "strategies": {
                "plaintiff": [
                    "Gather all property documents",
                    "Consult with a property lawyer",
                    "Verify title and ownership records"
                ],
                "defendant": [
                    "Review all claims and documents",
                    "Seek legal counsel",
                    "Prepare counter-documentation"
                ]
            },
            "confidence_score": 3,
            "next_steps": [
                "Consult with a qualified property lawyer in Bangalore",
                "Gather all relevant property documents",
                "Verify records with revenue authorities",
                "Consider mediation before litigation"
            ],
            "precedents": [
                {
                    "case": "Karnataka High Court precedents on property disputes",
                    "relevance": "Provides guidance on similar property matters in Karnataka"
                }
            ],
            "estimated_timeline": "6-18 months depending on case complexity and court proceedings",
            "estimated_costs": "₹1,00,000 - ₹5,00,000 including legal fees and court costs"
        }

# Create AI service instance
ai_service = AIService()

# Dependency to get AI service
def get_ai_service() -> AIService:
    return ai_service

# Main function for case analysis
async def analyze_case_with_ai(case_text: str, dispute_type: DisputeType) -> Dict[str, Any]:
    """Main function to analyze case with AI"""
    return await ai_service.analyze_case(case_text, dispute_type)
# Dependency to get AI service
def get_ai_service() -> AIService:
    return ai_service

# Main function for case analysis
async def analyze_case_with_ai(case_text: str, dispute_type: DisputeType) -> Dict[str, Any]:
    """Main function to analyze case with AI"""
    return await ai_service.analyze_case(case_text, dispute_type)
