"""
Agent Tools
Each tool does one specific job. The agent decides which to call.
"""
from app.services.rag_service import rag_service
from app.services.llm_service import ollama_service
from typing import Dict, List, Optional
import json


def extract_profile(text: str) -> Dict:
    """
    Extract applicant profile information from text.
    Returns structured data about the person.
    """
    prompt = f"""Extract immigration applicant information from this text.
Return ONLY a JSON object with these fields (use null if not found):
{{
    "full_name": "string or null",
    "email": "string or null", 
    "phone": "string or null",
    "nationality": "string or null",
    "current_status": "string or null",
    "employer": "string or null",
    "job_title": "string or null",
    "salary": "string or null",
    "education": "string or null",
    "visa_type_needed": "string or null"
}}

Text to analyze:
{text}

Return only the JSON, no explanation."""

    response = ollama_service.generate(prompt)
    
    try:
        # Clean response and parse JSON
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except:
        return {"raw_extraction": response, "parse_error": True}


def identify_visa_type(profile: Dict, situation: str) -> Dict:
    """
    Identify the appropriate visa type based on profile and situation.
    """
    prompt = f"""Based on this applicant profile and situation, identify the most appropriate US visa type.

Profile: {json.dumps(profile, indent=2)}
Situation: {situation}

Return ONLY a JSON object:
{{
    "visa_type": "e.g. H-1B, L-1, O-1, EB-2",
    "confidence": "high/medium/low",
    "reasoning": "brief explanation",
    "alternatives": ["other possible visas"]
}}

Return only the JSON."""

    response = ollama_service.generate(prompt)
    
    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except:
        return {"visa_type": "H-1B", "reasoning": response, "parse_error": True}


def retrieve_knowledge(query: str, visa_type: Optional[str] = None) -> List[Dict]:
    """
    Search the RAG knowledge base and return relevant chunks with citations.
    """
    results = rag_service.search(query, n_results=3)
    return results


def generate_checklist(visa_type: str, profile: Dict) -> Dict:
    """
    Generate a document checklist for the case.
    """
    # First get RAG context
    rag_results = rag_service.search(f"{visa_type} required documents checklist", n_results=3)
    rag_context = "\n".join([r['text'] for r in rag_results])
    
    prompt = f"""Generate a document checklist for a {visa_type} visa application.

Applicant profile:
{json.dumps(profile, indent=2)}

Knowledge base context:
{rag_context}

Return ONLY a JSON object:
{{
    "visa_type": "{visa_type}",
    "categories": [
        {{
            "name": "Personal Documents",
            "items": [
                {{"document": "Passport", "required": true, "notes": "Must be valid 6+ months"}},
                {{"document": "Birth Certificate", "required": false, "notes": "Recommended"}}
            ]
        }}
    ]
}}

Return only the JSON."""

    response = ollama_service.generate(prompt)
    
    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except:
        return {"visa_type": visa_type, "raw": response, "parse_error": True}


def draft_letter(letter_type: str, profile: Dict, case_details: str) -> str:
    """
    Draft a cover letter or support letter for the case.
    """
    prompt = f"""Write a professional {letter_type} for a US immigration case.

Applicant: {json.dumps(profile, indent=2)}
Case details: {case_details}

Write a complete, professional letter. Use proper legal language.
Include placeholders like [COMPANY LETTERHEAD] where needed."""

    return ollama_service.generate(prompt)


def summarize_case(messages: List[Dict], profile: Dict) -> str:
    """
    Summarize the entire case based on conversation history.
    """
    conversation = "\n".join([
        f"{m['role'].upper()}: {m['content']}"
        for m in messages[-10:]  # Last 10 messages
    ])
    
    prompt = f"""Summarize this immigration case intake conversation.

Conversation:
{conversation}

Known profile:
{json.dumps(profile, indent=2)}

Provide a concise summary covering:
1. Applicant background
2. Visa type needed
3. Key facts
4. Missing information still needed
5. Next steps"""

    return ollama_service.generate(prompt)