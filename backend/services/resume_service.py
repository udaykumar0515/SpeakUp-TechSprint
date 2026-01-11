import os
import uuid
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import ResumeResult
from datetime import datetime
from dotenv import load_dotenv
from firebase_config import firestore_client
from services.document_ai_ocr import extract_resume_text
from services.gemini_client import generate_structured_json

# Load environment variables
load_dotenv()

def analyze_resume_content(file_data: bytes):
    """
    Two-step AI-powered resume analysis:
    1. Document AI OCR → Extract text from PDF
    2. Gemini → Comprehensive ATS analysis (parsing, scoring, suggestions)
    """
    # STEP 1: Extract text from PDF using hybrid approach (pypdf + Document AI)
    print("📄 Step 1: Extracting text from PDF...")
    full_text = extract_resume_text(file_data)
    
    if not full_text or full_text.startswith("Unable to extract"):
        return {"error": full_text or "Failed to extract text from PDF"}
    
    print(f"✅ Extracted {len(full_text)} characters from PDF")
    
    # STEP 2: Send extracted text to Gemini for comprehensive analysis
    print("🧠 Step 2: Analyzing with Gemini (parsing + scoring + suggestions)...")
    analysis = analyze_with_gemini(full_text)
    
    if not analysis or "error" in analysis:
        return analysis or {"error": "Failed to analyze resume"}
    
    print("✅ Analysis complete!")
    return analysis

def analyze_with_gemini(resume_text: str):
    """
    Send extracted text to Gemini for comprehensive ATS analysis
    
    Returns:
        {
            "fullText": str,
            "parsedData": {...},
            "atsScore": int (0-100),
            "suggestions": [...]
        }
    """
    analysis_prompt = f"""You are an expert ATS (Applicant Tracking System) and professional HR recruiter analyzing a resume.

RESUME TEXT:
{resume_text}

TASK: Provide a comprehensive analysis of this resume. Respond in VALID JSON format with these exact keys:

{{
  "parsedData": {{
    "name": "Full name of candidate",
    "email": "Email address or 'Not found'",
    "phone": "Phone number or 'Not found'",
    "skills": ["list", "of", "all", "technical", "and", "soft", "skills"],
    "experience": "Brief summary of work experience (2-3 sentences highlighting key roles and achievements)",
    "education": "Education details (degrees, institutions, years)",
    "certifications": ["list", "of", "certifications"] or [],
    "summary": "Professional summary/objective if present, otherwise generate a compelling 2-3 line summary based on their background"
  }},
  "atsScore": <number between 0-100>,
  "suggestions": ["list", "of", "5-8", "actionable", "improvement", "suggestions"]
}}

SCORING CRITERIA (0-100):
- Contact info completeness (15 pts)
- Number and relevance of skills (20 pts)
- Experience detail and quantification (25 pts)
- Education clarity (15 pts)
- Use of action verbs and keywords (15 pts)
- Quantifiable achievements (numbers, percentages) (10 pts)

SUGGESTION GUIDELINES:
- Be specific and actionable
- Focus on ATS optimization
- Include formatting, keyword, and content improvements
- Prioritize high-impact changes
- Use emojis for better readability (✅, 💡, 📊, etc.)

Respond ONLY with valid JSON."""

    try:
        parsed = generate_structured_json(
            prompt=analysis_prompt,
            model_name="gemini-1.5-pro",  # Use Pro for better analysis
            temperature=0.3,
            max_output_tokens=2500
        )
        
        if not parsed:
            return {"error": "Failed to get response from Gemini"}
        
        # Ensure fullText is included
        parsed["fullText"] = resume_text
        
        return parsed
        
    except Exception as e:
        print(f"❌ Gemini analysis error: {str(e)}")
        return {"error": f"Gemini analysis error: {str(e)}"}

def save_result(result: ResumeResult):
    """Save resume result to Firestore"""
    from google.cloud.firestore_v1 import SERVER_TIMESTAMP
    
    result.id = str(uuid.uuid4())
    
    result_dict = result.model_dump()
    result_dict['createdAt'] = SERVER_TIMESTAMP
    
    firestore_client.collection('resume_results').document(result.id).set(result_dict)
    
    return result

def get_history(userId: str):
    """Get resume history from Firestore for a user (userId is Firebase UID)"""
    results = []
    docs = firestore_client.collection('resume_results')\
        .where('userId', '==', userId)\
        .stream()
    
    for doc in docs:
        data = doc.to_dict()
        results.append(ResumeResult(**data))
    
    # Sort in Python
    def get_sort_key(x):
        created = x.createdAt if x.createdAt else ''
        if hasattr(created, 'isoformat'):
            return created.isoformat()
        return str(created)
        
    results.sort(key=get_sort_key, reverse=True)
    return results
