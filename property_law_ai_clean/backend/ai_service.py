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
You are a legal AI assistant for Karnataka property law. Analyze the case and respond ONLY in valid JSON format.

Required JSON structure:
{
    "case_summary": {
        "facts": "Brief factual summary",
        "claims": "What parties claim",
        "dispute_nature": "Type of dispute"
    },
    "legal_issues": ["Key legal questions"],
    "applicable_laws": [
        {"law": "Law name", "relevance": "How it applies"}
    ],
    "missing_evidence": ["Required documents"],
    "strategies": {
        "plaintiff": ["Plaintiff strategies"],
        "defendant": ["Defendant strategies"]
    },
    "confidence_score": 7,
    "next_steps": ["Recommended actions"],
    "estimated_timeline": "Duration estimate",
    "estimated_costs": "Cost estimate"
}

Confidence Score Guidelines:
- 8-10: Clear facts, straightforward law, minimal missing evidence
- 6-7: Good facts, established law, some missing documents
- 4-5: Adequate facts, complex issues, significant missing evidence
- 1-3: Unclear facts, very complex legal issues, major gaps

For inheritance cases with clear family structure and established law, score should be 6-8.
Analyze each case individually based on the specific facts provided.
"""

def create_user_prompt(case_text: str, dispute_type: str) -> str:
    """Create user prompt for case analysis"""
    return f"""
Analyze this property law case for Bangalore, Karnataka:

Case Details: {case_text}
Dispute Type: {dispute_type}

Provide analysis in the exact JSON format specified. Focus on the specific facts of this case.
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
            
            # Create prompt with clear instructions
            full_prompt = f"{BANGALORE_PROPERTY_LAW_SYSTEM_PROMPT}\n\n{create_user_prompt(case_text, dispute_type.value)}\n\nRespond with complete valid JSON only. Do not use markdown formatting."
            
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
                        max_output_tokens=2048,
                        candidate_count=1,
                        stop_sequences=None
                    )
                )
            )
            
            if response.text:
                return response.text
            else:
                logger.error("Empty response from Gemini API")
                raise Exception("Empty response from Gemini API")
            
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            raise Exception(f"Gemini API request failed: {str(e)}")

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        try:
            # Clean response text - remove markdown code blocks if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # If response is empty or just markdown, return fallback
            if not cleaned_text or cleaned_text == '```json' or cleaned_text == '```':
                logger.error("Empty or incomplete response from Gemini")
                return self._create_fallback_response(response_text)
            
            # Try to parse JSON
            ai_response = json.loads(cleaned_text)
            
            # Validate and fix structure
            if not isinstance(ai_response.get("case_summary"), dict):
                ai_response["case_summary"] = {
                    "facts": "Case analysis completed",
                    "claims": "Legal claims identified",
                    "dispute_nature": "Property dispute"
                }
            
            # Ensure required fields exist
            ai_response.setdefault("legal_issues", ["Property law analysis required"])
            ai_response.setdefault("applicable_laws", [{"law": "Karnataka Land Revenue Act", "relevance": "Property matters"}])
            ai_response.setdefault("missing_evidence", ["Property documents"])
            ai_response.setdefault("strategies", {"plaintiff": ["Legal consultation"], "defendant": ["Document review"]})
            # Ensure confidence score is reasonable
            confidence = ai_response.get("confidence_score", 6)
            if isinstance(confidence, (int, float)) and 1 <= confidence <= 10:
                ai_response["confidence_score"] = int(confidence)
            else:
                ai_response["confidence_score"] = 6
            ai_response.setdefault("next_steps", ["Consult legal expert"])
            ai_response.setdefault("estimated_timeline", "3-6 months")
            ai_response.setdefault("estimated_costs", "₹50,000 - ₹2,00,000")
            
            return ai_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: '{response_text}'")
            logger.error(f"Cleaned text: '{cleaned_text}'")
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
