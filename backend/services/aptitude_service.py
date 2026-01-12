import os
import json
import uuid
import random
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import AptitudeResult
from datetime import datetime
from dotenv import load_dotenv
from firebase_config import firestore_client
from services.gemini_client import get_gpt_response

# Load environment variables
load_dotenv()

def load_questions_from_json(topic: str):
    """Load questions from JSON file"""
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", f"{topic.lower()}_questions.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading questions from {file_path}: {e}")
        return []

def shuffle_question_options(question):
    """Shuffle options and update correctAnswer index"""
    q_copy = question.copy()
    correct_text = q_copy['options'][q_copy['correctAnswer']]
    
    # Shuffle options
    random.shuffle(q_copy['options'])
    
    # Update correctAnswer to new index
    q_copy['correctAnswer'] = q_copy['options'].index(correct_text)
    
    return q_copy

def get_random_questions(topic: str, count: int = 20):
    """Get random questions with shuffled options"""
    all_questions = load_questions_from_json(topic)
    
    if not all_questions:
        return []
    
    # Select random questions (or all if count > available)
    num_to_select = min(count, len(all_questions))
    selected = random.sample(all_questions, num_to_select)
    
    # Shuffle options for each question
    shuffled = [shuffle_question_options(q) for q in selected]
    
    return shuffled

def get_ai_powered_questions(topic: str):
    """Generate 3 hard questions using Gemini - NO FALLBACK"""
    # Very simple prompt to avoid truncation and LaTeX
    prompt = f"""Create 3 challenging {topic} test questions.

IMPORTANT: Write ALL math in plain text. NO LaTeX, NO dollar signs, NO special notation.
Examples:
- Write "2/3" NOT "$\\frac{{2}}{{3}}$"
- Write "x^2" NOT "$x^2$"
- Write "sqrt(16)" NOT "$\\sqrt{{16}}$"

Return ONLY this JSON array (no explanations):
[
  {{
    "question": "plain text question here",
    "options": ["A", "B", "C", "D"],
    "correctAnswer": 0
  }}
]

Topic: {topic}"""
    
    messages = [
        {"role": "system", "content": "Return ONLY a JSON array. No markdown, no explanations."},
        {"role": "user", "content": prompt}
    ]
    
    # Use gemini_client with higher token limit
    from services.gemini_client import generate_text
    
    content = generate_text(prompt=prompt, max_output_tokens=2000, json_mode=True)
    
    try:
        if not content:
            print("❌ No response from Gemini")
            return []
        
        print(f"🔍 RAW Response ({len(content)} chars): {content[:200]}...")
        
        # Extract JSON array FIRST, then clean
        start = content.find("[")
        end = content.rfind("]") + 1
        
        if start == -1 or end <= start:
            print("❌ No JSON array found in response")
            return []
        
        content = content[start:end]
        # NOW remove any markdown that might be inside
        content = content.replace("```json", "").replace("```", "").strip()

        print(f"🔍 Extracted JSON: {content[:300]}...")
        
        questions = json.loads(content)
        
        # Validate structure
        if not isinstance(questions, list):
            print(f"❌ Response is not a list: {type(questions)}")
            return []
            
        if len(questions) == 0:
            print("❌ Empty questions list")
            return []
        
        # Add IDs and validate each question
        valid_questions = []
        for i, q in enumerate(questions):
            if (isinstance(q, dict) and 
                'question' in q and 
                'options' in q and 
                isinstance(q['options'], list) and 
                len(q['options']) == 4):
                q['id'] = i + 1
                if 'correctAnswer' not in q:
                    q['correctAnswer'] = 0
                if 'explanation' not in q:
                    q['explanation'] = "Answer explanation"
                valid_questions.append(q)
                print(f"✅ Valid Q{i+1}: {q['question'][:60]}...")
            else:
                print(f"❌ Invalid Q{i+1} structure")
        
        if len(valid_questions) < 3:
            print(f"❌ Only got {len(valid_questions)}/3 valid questions - FAILING (no fallback)")
            return []
        
        print(f"✅ SUCCESS: Generated {len(valid_questions)} AI questions")
        return valid_questions[:3]
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        if 'content' in locals():
            print(f"Content: {content[:500]}")
        return []
    except Exception as e:
        print(f"❌ Error generating AI questions: {e}")
        import traceback
        traceback.print_exc()
        return []

def submit_test(userId: int, topic: str, questions: list, answers: list, timeTaken: int = 0):
    """
    Submit aptitude test answers and generate comprehensive results
    """
    from datetime import datetime
    
    # Calculate results
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    question_breakdown = []
    
    for idx, question in enumerate(questions):
        # Handle both list (frontend) and dict (legacy) formats
        if isinstance(answers, list):
            user_answer = answers[idx] if idx < len(answers) else None
        else:
            question_id = question.get("id", str(idx))
            user_answer = answers.get(str(question_id))
        
        correct_answer = question.get("correctAnswer", 0)
        
        is_correct = user_answer == correct_answer if user_answer is not None else False
        
        if user_answer is None:
            unanswered_count += 1
            status = "unanswered"
        elif is_correct:
            correct_count += 1
            status = "correct"
        else:
            incorrect_count += 1
            status = "incorrect"
        
        question_breakdown.append({
            "questionNumber": idx + 1,
            "questionText": question.get("question", ""),
            "options": question.get("options", []),
            "correctAnswer": correct_answer,
            "userAnswer": user_answer,
            "status": status,
            "explanation": question.get("explanation", "")
        })
    
    # Calculate score
    total_questions = len(questions)
    score_percentage = round((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    # Calculate completion metrics
    questions_answered = total_questions - unanswered_count
    completion_percentage = round((questions_answered / total_questions) * 100) if total_questions > 0 else 0
    
    # Determine performance level
    if score_percentage >= 90:
        performance_level = "Excellent"
    elif score_percentage >= 75:
        performance_level = "Good"
    elif score_percentage >= 60:
        performance_level = "Average"
    else:
        performance_level = "Needs Improvement"
    
    # Create result object
    result = AptitudeResult(
        id=str(uuid.uuid4()),
        userId=userId,
        topic=topic,
        score=score_percentage,
        totalQuestions=total_questions,
        accuracy=score_percentage,
        timeTaken=timeTaken,
        correctAnswers=correct_count,
        incorrectAnswers=incorrect_count,
        unansweredQuestions=unanswered_count,
        performanceLevel=performance_level,
        createdAt=datetime.now().isoformat()
    )
    
    # Save to Firestore
    try:
        firestore_client.collection('aptitude_results').document(result.id).set(result.model_dump())
        print(f"✅ Aptitude result saved to Firestore: {result.id}")
    except Exception as e:
        print(f"❌ Failed to save to Firestore: {str(e)}")
    
    # Return comprehensive results
    return {
        "id": result.id,
        "topic": topic,
        "score": score_percentage,
        "totalQuestions": total_questions,
        "correctAnswers": correct_count,
        "incorrectAnswers": incorrect_count,
        "unansweredQuestions": unanswered_count,
        "accuracy": score_percentage,
        "timeTaken": timeTaken,
        "createdAt": result.createdAt,
        "completionMetrics": {
            "questionsAnswered": questions_answered,
            "totalQuestions": total_questions,
            "completionPercentage": completion_percentage,
            "timeTakenMinutes": round(timeTaken / 60) if timeTaken > 0 else 0,
            "isFullyCompleted": unanswered_count == 0
        },
        "questionBreakdown": question_breakdown,
        "performanceLevel": (
            "Excellent" if score_percentage >= 90 else
            "Very Good" if score_percentage >= 75 else
            "Good" if score_percentage >= 60 else
            "Average" if score_percentage >= 50 else
            "Needs Improvement"
        )
    }

def save_result(result: AptitudeResult):
    """Save aptitude result to Firestore"""
    result.id = str(uuid.uuid4())
    
    result_dict = result.model_dump()
    from google.cloud.firestore_v1 import SERVER_TIMESTAMP
    result_dict['createdAt'] = SERVER_TIMESTAMP
    
    firestore_client.collection('aptitude_results').document(result.id).set(result_dict)
    
    return result

def get_history(userId: str):
    """Get users aptitude history from Firestore
    # Note: Removed order_by to avoid composite index requirement
    # Sorting is done in Python instead
    """
    results = firestore_client.collection('aptitude_results')\
        .where('userId', '==', userId)\
        .stream()
    
    history = [doc.to_dict() for doc in results]
    # Sort by createdAt in Python (descending)
    def get_sort_key(x):
        created = x.get('createdAt', '')
        if hasattr(created, 'isoformat'):
            return created.isoformat()
        return str(created)
        
    history.sort(key=get_sort_key, reverse=True)
    return history
