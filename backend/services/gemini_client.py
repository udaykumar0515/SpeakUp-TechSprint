import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional
import time

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ WARNING: GEMINI_API_KEY not found in environment variables")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured successfully")

# Available models - using latest stable versions
GEMINI_FLASH = "gemini-flash-latest"  # Fast, cost-effective
GEMINI_PRO = "gemini-pro-latest"      # Advanced reasoning

def _safe_extract_text(response) -> str:
    """
    Safely extract text from Gemini response without using response.text accessor.
    Handles cases where finish_reason=2 (MAX_TOKENS) returns empty parts.
    
    Returns:
        Extracted text or empty string if no valid parts found
    """
    if not response or not getattr(response, "candidates", None):
        return ""
    
    cand = response.candidates[0]
    content = getattr(cand, "content", None)
    if not content or not getattr(content, "parts", None):
        return ""
    
    texts = []
    for part in content.parts:
        if hasattr(part, "text") and part.text:
            texts.append(part.text)
    
    return "".join(texts).strip()

def generate_text(
    prompt: str,
    model_name: str = GEMINI_FLASH,
    temperature: float = 0.7,
    max_output_tokens: int = 2048,
    json_mode: bool = False,
    max_retries: int = 3
) -> Optional[str]:
    """
    Generate text using Gemini API with retry logic
    
    Args:
        prompt: The input prompt
        model_name: Model to use (gemini-flash-latest or gemini-pro-latest)
        temperature: Creativity (0.0-1.0)
        max_output_tokens: Maximum response length
        json_mode: If True, instructs model to return JSON
        max_retries: Number of retry attempts
        
    Returns:
        Generated text or None if failed
    """
    if not GEMINI_API_KEY:
        print("❌ Gemini API key not configured")
        return None
    
    # Add JSON instruction to prompt if needed
    if json_mode:
        prompt = f"{prompt}\n\nRespond with ONLY valid JSON, no markdown formatting or code blocks."
    
    generation_config = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    
    if json_mode:
        generation_config["response_mime_type"] = "application/json"
    
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            
            response = model.generate_content(prompt)
            
            # Check if response has candidates
            if not response.candidates:
                print(f"⚠️ No candidates in response (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
            
            # Check finish reason
            candidate = response.candidates[0]
            finish_reason = candidate.finish_reason
            
            # finish_reason values:
            # 0 = FINISH_REASON_UNSPECIFIED
            # 1 = STOP (normal completion)
            # 2 = MAX_TOKENS
            # 3 = SAFETY
            # 4 = RECITATION
            # 5 = OTHER
            
            # Safely extract text
            extracted_text = _safe_extract_text(response)
            
            # Log finish reason and extracted length for debugging
            if finish_reason != 1:  # Not normal completion
                print(f"🔍 finish_reason={finish_reason}, extracted_len={len(extracted_text)}")
            
            if finish_reason == 3:  # SAFETY
                print(f"⚠️ Response blocked by safety filters (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
            
            if finish_reason == 2:  # MAX_TOKENS - partial response
                if extracted_text:
                    print(f"⚠️ MAX_TOKENS hit but got {len(extracted_text)} chars - returning partial")
                    return extracted_text
                else:
                    print(f"⚠️ MAX_TOKENS hit with empty extraction - retrying (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                    continue
            
            # Normal response or other finish reasons
            if extracted_text:
                return extracted_text
            else:
                print(f"⚠️ Empty extraction from Gemini (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                
        except Exception as e:
            print(f"❌ Gemini API error (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            
    print(f"❌ All {max_retries} attempts failed")
    return None

def generate_structured_json(
    prompt: str,
    model_name: str = GEMINI_FLASH,
    temperature: float = 0.3,
    max_output_tokens: int = 2048,
    max_retries: int = 3
) -> Optional[dict]:
    """
    Generate structured JSON response using Gemini
    
    Returns:
        Parsed JSON dict or None if failed
    """
    response_text = generate_text(
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        json_mode=True,
        max_retries=max_retries
    )
    
    if not response_text:
        return None
    
    try:
        # Clean potential markdown formatting
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "").strip()
            
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"Response was: {response_text[:200]}...")
        return None

# For backward compatibility with existing code
def get_gpt_response(messages: list, model: str = None, max_tokens: int = 1500) -> Optional[dict]:
    """
    Legacy function compatibility layer - converts OpenAI-style messages to Gemini
    
    Args:
        messages: List of {"role": "user/system", "content": "..."}
        model: Ignored (uses Gemini)
        max_tokens: Maximum output length
        
    Returns:
        OpenAI-compatible response dict or None
    """
    # Combine messages into single prompt
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"Instructions: {content}")
        else:
            prompt_parts.append(content)
    
    full_prompt = "\n\n".join(prompt_parts)
    
    response_text = generate_text(
        prompt=full_prompt,
        model_name=GEMINI_FLASH,
        max_output_tokens=max_tokens
    )
    
    if not response_text:
        return None
    
    # Return in OpenAI-compatible format
    return {
        "choices": [
            {
                "message": {
                    "content": response_text,
                    "role": "assistant"
                }
            }
        ]
    }
