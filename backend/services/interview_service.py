import os
import json
import uuid
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import InterviewSession, InterviewResult
from datetime import datetime
from dotenv import load_dotenv
from firebase_config import firestore_client
from services.gemini_client import get_gpt_response

# Load environment variables
load_dotenv()

# Global In-Memory Storage (Sessions only - Results go to Firestore)
INTERVIEW_SESSIONS = {}

def start_new_session(userId: int, interviewType: str, difficulty: str, mode: str, jobRole: str = "Software Engineer", resumeData: dict = None):
    """
    Start a new AI-powered interview session
    
    Args:
        userId: User ID
        interviewType: technical, hr, behavioral
        difficulty: junior, mid, senior
        mode: practice, graded
        jobRole: Target job role (e.g. "Product Manager")
        resumeData: Optional resume data from Resume Analyzer
    """
    sessionId = str(uuid.uuid4())
    
    # Generate dynamic questions using GPT-4 Full
    print(f"🎯 Generating interview questions: {interviewType} / {difficulty} level for {jobRole}")
    questions = generate_questions(interviewType, difficulty, resumeData)
    
    # Create session
    session = {
        "sessionId": sessionId,
        "userId": userId,
        "interviewType": interviewType,
        "difficulty": difficulty,
        "mode": mode,
        "resumeData": resumeData,
        "questions": questions,
        "answers": [],
        "greetingGiven": False,
        "greetingBonus": 0,
        "currentQuestionIndex": 0,
        "isComplete": False,
        "startTime": datetime.now().isoformat()
    }
    
    INTERVIEW_SESSIONS[sessionId] = session
    
    return {
        "sessionId": sessionId,
        "totalQuestions": len(questions),
        "greetingPrompt": "You may greet the interviewer to start. For example: 'Good morning, sir!'",
        "interviewType": interviewType,
        "difficulty": difficulty,
        "mode": mode
    }

def generate_questions(interview_type: str, difficulty: str, resume_data: dict = None) -> list:
    """
    Use Gemini to generate 8-12 dynamic interview questions
    """
    # Build context from resume if available
    resume_context = ""
    if resume_data:
        skills = resume_data.get("parsedData", {}).get("skills", [])
        experience = resume_data.get("parsedData", {}).get("experience", "")
        resume_context = f"\nCandidate's Skills: {', '.join(skills[:10])}\nExperience: {experience[:200]}"
    
    prompt = f"""You are an expert interviewer conducting a {interview_type.upper()} interview at {difficulty.upper()} level.

{resume_context}

TASK: Generate 8-12 high-quality interview questions that:
1. Match the {difficulty} difficulty level (junior=easier, senior=harder)
2. Focus on {interview_type} topics
3. Include resume-specific questions if resume data is provided
4. Progress from easier to harder
5. Test real-world skills and understanding

Interview Types Guide:
- TECHNICAL: Coding, system design, algorithms, tech stack
- HR: Leadership, teamwork, conflict resolution, work ethic
- BEHAVIORAL: STAR method scenarios, past experiences, problem-solving

Difficulty Levels:
- JUNIOR: Basic concepts, simple scenarios
- MID: Intermediate complexity, some depth
- SENIOR: Advanced concepts, complex scenarios, leadership

CRITICAL: Return ONLY a valid JSON array of strings. No markdown, no explanations.
Format: ["Question 1", "Question 2", ...]

JSON Response:"""

    try:
        messages = [
            {"role": "system", "content": "You are an expert interviewer. Always respond with valid JSON only - a simple array of question strings."},
            {"role": "user", "content": prompt}
        ]
        
        resp = get_gpt_response(messages, model=None, max_tokens=1200)
        if resp and 'choices' in resp:
            content = resp['choices'][0]['message']['content'].strip()
            
            # Aggressive cleaning
            content = content.replace("```json", "").replace("```", "").strip()
            # Remove any leading/trailing text
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end > start:
                content = content[start:end]
            
            # Try to parse
            questions_list = json.loads(content)
            
            # Validate it's a list of strings
            if not isinstance(questions_list, list):
                raise ValueError("Response is not a list")
            
            # Filter to only strings
            questions_list = [q for q in questions_list if isinstance(q, str) and len(q.strip()) > 10]
            
            # Ensure 8-12 questions
            if len(questions_list) < 8:
                questions_list = questions_list + get_fallback_questions(interview_type, difficulty)[:(8-len(questions_list))]
            elif len(questions_list) > 12:
                questions_list = questions_list[:12]
            
            return [{"id": str(uuid.uuid4()), "text": q} for q in questions_list]
    except json.JSONDecodeError as je:
        print(f"❌ JSON Parse Error: {je}")
        print(f"Content snippet: {content[:200] if 'content' in locals() else 'N/A'}...")
    except Exception as e:
        print(f"❌ Question generation error: {e}")
    
    # Fallback to predefined questions
    print("🔄 Using fallback questions")
    return get_fallback_questions(interview_type, difficulty)

def get_fallback_questions(interview_type: str, difficulty: str) -> list:
    """Fallback questions if AI generation fails"""
    questions_bank = {
        "technical": {
            "junior": [
                "What is the difference between a list and a tuple in Python?",
                "Explain what a REST API is.",
                "What is version control and why is it important?",
                "Describe the concept of object-oriented programming.",
                "What is the difference between GET and POST requests?",
                "How do you handle errors in your code?",
                "What is a database index?",
                "Explain the concept of inheritance."
            ],
            "mid": [
                "Design a simple URL shortener service.",
                "How would you optimize a slow database query?",
                "Explain the CAP theorem.",
                "What are design patterns? Give examples.",
                "How do you ensure code quality in a team?",
                "Explain async/await and when to use it.",
                "What is dependency injection?",
                "How would you design a caching system?"
            ],
            "senior": [
                "Design a scalable real-time chat system like WhatsApp.",
                "How would you handle millions of concurrent requests?",
                "Explain different types of load balancing strategies.",
                "Design a distributed rate limiter.",
                "How do you ensure data consistency in microservices?",
                "Explain your approach to technical debt.",
                "How would you migrate a monolith to microservices?",
                "Design a fault-tolerant payment processing system."
            ]
        },
        "hr": {
            "junior": [
                "Tell me about yourself.",
                "Why do you want to work here?",
                "What are your greatest strengths?",
                "Describe a challenge you faced and how you handled it.",
                "Where do you see yourself in 5 years?",
                "Why should we hire you?",
                "What motivates you?",
                "How do you handle criticism?"
            ],
            "mid": [
                "Describe a time you led a team project.",
                "How do you prioritize tasks when everything is urgent?",
                "Tell me about a conflict with a coworker and how you resolved it.",
                "Describe a time you failed. What did you learn?",
                "How do you handle difficult stakeholders?",
                "What's your management style?",
                "How do you mentor junior team members?",
                "Describe a time you had to make a difficult decision."
            ],
            "senior": [
                "How do you build and scale high-performing teams?",
                "Describe your approach to organizational change management.",
                "How do you align team goals with business objectives?",
                "Tell me about a time you influenced cross-functional teams.",
                "How do you handle underperforming team members?",
                "What's your strategy for driving innovation?",
                "How do you balance technical debt with new features?",
                "Describe your approach to conflict resolution at scale."
            ]
        },
        "behavioral": [
            "Describe a time you had to learn something completely new quickly.",
            "Tell me about a time you disagreed with your manager.",
            "Describe a situation where you had to work with limited resources.",
            "Tell me about your biggest professional achievement.",
            "Describe a time you made a mistake. How did you handle it?",
            "Tell me about a time you had to meet a tight deadline.",
            "Describe a situation where you had to adapt to change.",
            "Tell me about a time you went above and beyond."
        ]
    }
    
    if interview_type == "behavioral":
        selected = questions_bank["behavioral"][:10]
    else:
        selected = questions_bank.get(interview_type, {}).get(difficulty, questions_bank["technical"]["junior"])[:10]
    
    return [{"id": str(uuid.uuid4()), "text": q} for q in selected]

def process_greeting(sessionId: str, message: str):
    """
    Process user's greeting and award bonus points
    """
    session = INTERVIEW_SESSIONS.get(sessionId)
    if not session:
        return {"error": "Session not found"}
    
    # Check if greeting already given
    if session["greetingGiven"]:
        return {
            "acknowledged": False,
            "message": "Greeting already recorded. Let's begin the interview.",
            "firstQuestion": session["questions"][0]["text"],
            "progress": 0
        }
    
    # Detect professional greeting
    msg_lower = message.lower()
    greeting_keywords = ["good morning", "good afternoon", "good evening", "hello", "hi", "greetings"]
    professional_terms = ["sir", "ma'am", "interviewer", "team"]
    
    is_greeting = any(kw in msg_lower for kw in greeting_keywords)
    is_professional = any(term in msg_lower for term in professional_terms)
    
    if is_greeting:
        session["greetingGiven"] = True
        if is_professional:
            session["greetingBonus"] = 5  # Extra points for professional greeting
            response = "Good morning! I appreciate your professionalism. Let's get started with the interview."
        else:
            session["greetingBonus"] = 2  # Basic greeting
            response = "Hello! Let's begin the interview."
        
        return {
            "acknowledged": True,
            "response": response,
            "greetingBonus": session["greetingBonus"],
            "firstQuestion": session["questions"][0]["text"],
            "progress": 0
        }
    else:
        # Not a greeting, treat as first answer
        return process_answer(sessionId, message)

def process_answer(sessionId: str, answer: str):
    """
    Process user's answer and move to next question
    """
    session = INTERVIEW_SESSIONS.get(sessionId)
    if not session:
        return {"error": "Session not found"}
    
    idx = session["currentQuestionIndex"]
    
    if idx >= len(session["questions"]):
        return {"error": "Interview already complete"}
    
    # Record answer
    current_question = session["questions"][idx]
    session["answers"].append({
        "questionId": current_question["id"],
        "questionText": current_question["text"],
        "userAnswer": answer,
        "timestamp": datetime.now().isoformat()
    })
    
    session["currentQuestionIndex"] += 1
    
    # Calculate progress
    progress = (session["currentQuestionIndex"] / len(session["questions"])) * 100
    
    # Check if interview is complete
    if session["currentQuestionIndex"] >= len(session["questions"]):
        session["isComplete"] = True
        return {
            "isComplete": True,
            "progress": 100,
            "message": "Interview complete! Generating your results..."
        }
    
    # Return next question with brief acknowledgment
    acknowledgments = [
        "Okay. Next question:",
        "Understood. Moving on:",
        "Noted. Here's the next one:",
        "Got it. Next:",
        "Alright. Let's continue:"
    ]
    
    import random
    ack = random.choice(acknowledgments)
    next_question = session["questions"][session["currentQuestionIndex"]]["text"]
    
    return {
        "isComplete": False,
        "acknowledgment": ack,
        "nextQuestion": next_question,
        "questionNumber": session["currentQuestionIndex"] + 1,
        "progress": round(progress, 1)
    }

def end_interview(sessionId: str, userId: int):
    """
    End interview and generate comprehensive results with completion tracking
    """
    session = INTERVIEW_SESSIONS.get(sessionId)
    if not session:
        return {"error": "Session not found"}
    
    # IDEMPOTENCY CHECK with POLLING
    # If session is marked complete but result isn't ready, wait for it (handle race condition)
    if session.get("isComplete"):
        print(f"⚠️ Session {sessionId} in progress or completed. Waiting for result...")
        import time
        for _ in range(30):  # Wait up to 30 seconds
            if "finalResult" in session:
                return session["finalResult"]
            time.sleep(1)
        
        # If still no result after timeout, check if we should proceed or error
        # If we return error here, it's a 404 which breaks UI.
        # Ideally, we return the session state or a "processing" message, but frontend expects result.
        # Fallback: try to return what we have or just error gracefully.
        return {"error": "Session completion timed out"}

    # Mark as complete immediately to block other requests
    session["isComplete"] = True
    
    # Calculate completion metrics
    questions_answered = len(session.get("answers", []))
    total_questions = len(session.get("questions", []))
    if total_questions == 0:
        total_questions = 10 # Fallback default
        
    completion_percentage = round((questions_answered / total_questions) * 100)
    
    # Calculate session duration
    from datetime import datetime
    start_time = session.get("startTime")
    if isinstance(start_time, str):
        from dateutil import parser
        start_time = parser.parse(start_time)
    
    session_duration_seconds = (datetime.now() - start_time).total_seconds() if start_time else 0
    session_duration_minutes = round(session_duration_seconds / 60)
    
    # Generate overall feedback and scores using GPT-4 Full
    print(f"📊 Generating comprehensive interview feedback... ({questions_answered}/{total_questions} questions, {completion_percentage}% complete)")
    
    if session["mode"] == "graded":
        result = generate_graded_results(session)
    else:  # practice mode
        result = generate_practice_results(session)
    
    # Add completion tracking to result
    result["completionMetrics"] = {
        "questionsAnswered": questions_answered,
        "totalQuestions": total_questions,
        "completionPercentage": completion_percentage,
        "sessionDurationMinutes": session_duration_minutes,
        "isFullyCompleted": questions_answered >= total_questions
    }

    # PERSISTENCE: Save result to Firestore
    try:
        if session["mode"] != "practice":
            metrics = result.get("metrics", {})
            
            # Map detailed metrics to flat structure for DB
            interview_res = InterviewResult(
                userId=userId,
                communicationScore=metrics.get("communicationClarity", 0),
                confidenceScore=metrics.get("confidence", 0),
                relevanceScore=metrics.get("depthOfUnderstanding", 0), # Mapping Understanding -> Relevance
                feedback=result.get("overallFeedback", "Interview completed."),
                interviewType=session["interviewType"],
                jobRole=session.get("jobRole", "General"),
                questionCount=questions_answered,
                sessionDuration=session_duration_minutes
            )
            
            print(f"💾 Automatically saving interview result for session {sessionId}")
            save_result(interview_res)
            
            # Add the saved ID to return value if needed
            result["id"] = interview_res.id
        else:
            print(f"⏩ Practice mode session {sessionId}: Skipping persistence as requested.")
            result["id"] = "temporary-practice-id"
        
    except Exception as e:
        print(f"❌ Failed to auto-save interview result: {e}")
    
    # Cache result to support idempotency check
    session["finalResult"] = result
    return result

def generate_graded_results(session: dict) -> dict:
    """
    Generate results with scores for graded mode
    """
    if not session.get("answers"):
        return get_fallback_evaluation(session, graded=True)

    # Build context for GPT-4
    qa_context = "\n\n".join([
        f"Q{i+1}: {ans['questionText']}\nAnswer: {ans['userAnswer']}"
        for i, ans in enumerate(session["answers"])
    ])
    
    prompt = f"""You are an expert interview evaluator for a {session['interviewType'].upper()} interview at {session['difficulty'].upper()} level.

INTERVIEW TRANSCRIPT:
{qa_context}

TASK: Provide comprehensive evaluation in VALID JSON format:

{{
  "overallScore": <0-100>,
  "overallFeedback": "Detailed 3-4 sentence overall assessment",
  "metrics": {{
    "technicalAccuracy": <0-100>,
    "communicationClarity": <0-100>,
    "confidence": <0-100>,
    "depthOfUnderstanding": <0-100>
  }},
  "strengths": ["strength1", "strength2", "strength3"],
  "areasForImprovement": ["area1", "area2", "area3"],
  "questionBreakdown": [
    {{
      "questionNumber": 1,
      "score": <0-10>,
      "feedback": "Specific feedback for this answer"
    }}
  ]
}}

Scoring Criteria:
- Technical Accuracy: Correctness of information
- Communication: Clarity, structure, conciseness
- Confidence: Tone, decisiveness, conviction
- Understanding: Depth, examples, real-world application

JSON Response:"""

    try:
        messages = [
            {"role": "system", "content": "You are an expert interview evaluator. Respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        resp = get_gpt_response(messages, model=None, max_tokens=2000)
        if resp and 'choices' in resp:
            content = resp['choices'][0]['message']['content'].strip()
            
            # Clean markdown
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            evaluation = json.loads(content)
            
            # Add greeting bonus to overall score
            overall_score = evaluation.get("overallScore", 75)
            overall_score = min(100, overall_score + session.get("greetingBonus", 0))
            evaluation["overallScore"] = overall_score
            evaluation["greetingBonus"] = session.get("greetingBonus", 0)
            
            # Add question texts to breakdown
            for i, item in enumerate(evaluation.get("questionBreakdown", [])):
                if i < len(session["answers"]):
                    item["questionText"] = session["answers"][i]["questionText"]
                    item["userAnswer"] = session["answers"][i]["userAnswer"]
                    item["questionId"] = session["answers"][i]["questionId"]
            
            return evaluation
    except Exception as e:
        print(f"Evaluation error: {e}")
    
    # Fallback evaluation
    return get_fallback_evaluation(session, graded=True)

def generate_practice_results(session: dict) -> dict:
    """
    Generate results with feedback only (no scores) for practice mode
    """
    if not session.get("answers"):
        return get_fallback_evaluation(session, graded=False)

    # Similar to graded but without scores
    qa_context = "\n\n".join([
        f"Q{i+1}: {ans['questionText']}\nAnswer: {ans['userAnswer']}"
        for i, ans in enumerate(session["answers"])
    ])
    
    prompt = f"""You are a supportive interview coach for a {session['interviewType'].upper()} interview at {session['difficulty'].upper()} level.

INTERVIEW TRANSCRIPT:
{qa_context}

TASK: Provide encouraging, constructive feedback in VALID JSON:

{{
  "overallFeedback": "Encouraging 3-4 sentence overall assessment focusing on growth",
  "strengths": ["strength1", "strength2", "strength3"],
  "areasForImprovement": ["area1", "area2", "area3"],
  "actionableadvice": ["tip1", "tip2", "tip3"],
  "questionBreakdown": [
    {{
      "questionNumber": 1,
      "feedback": "Constructive, specific feedback for this answer",
      "improvementTips": ["tip1", "tip2"]
    }}
  ]
}}

Focus on:
- What they did well
- Specific ways to improve
- Actionable next steps
- Encouraging tone

JSON Response:"""

    try:
        messages = [
            {"role": "system", "content": "You are a supportive interview coach. Respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        resp = get_gpt_response(messages, model=None, max_tokens=2000)
        if resp and 'choices' in resp:
            content = resp['choices'][0]['message']['content'].strip()
            
            # Clean markdown
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            evaluation = json.loads(content)
            
            # Add question texts to breakdown
            for i, item in enumerate(evaluation.get("questionBreakdown", [])):
                if i < len(session["answers"]):
                    item["questionText"] = session["answers"][i]["questionText"]
                    item["userAnswer"] = session["answers"][i]["userAnswer"]
                    item["questionId"] = session["answers"][i]["questionId"]
            
            evaluation["mode"] = "practice"
            evaluation["greetingBonus"] = session.get("greetingBonus", 0)
            
            return evaluation
    except Exception as e:
        print(f"Evaluation error: {e}")
    
    # Fallback
    return get_fallback_evaluation(session, graded=False)

def get_fallback_evaluation(session: dict, graded: bool = True) -> dict:
    """Fallback evaluation if AI fails or no data"""
    has_answers = len(session.get("answers", [])) > 0
    
    base = {
        "overallFeedback": "No feedback available. Please complete the interview." if not has_answers else "Evaluation service unavailable. Please try again.",
        "strengths": [] if not has_answers else ["Participation"],
        "areasForImprovement": ["Complete the interview to receive evaluation."] if not has_answers else ["Retry submission"],
        "questionBreakdown": []
    }
    
    for i, ans in enumerate(session.get("answers", [])):
        breakdown_item = {
            "questionNumber": i + 1,
            "questionText": ans["questionText"],
            "userAnswer": ans["userAnswer"],
            "questionId": ans["questionId"],
            "feedback": "Feedback unavailable."
        }
        
        if graded:
            breakdown_item["score"] = 0
        else:
            breakdown_item["improvementTips"] = []
        
        base["questionBreakdown"].append(breakdown_item)
    
    if graded:
        base["overallScore"] = 0 + session.get("greetingBonus", 0)
        base["metrics"] = {
            "technicalAccuracy": 0,
            "communicationClarity": 0,
            "confidence": 0,
            "depthOfUnderstanding": 0
        }
        base["greetingBonus"] = session.get("greetingBonus", 0)
    else:
        base["mode"] = "practice"
        base["actionableadvice"] = ["Complete more questions"]
    
    return base

def get_teach_me(questionId: str, questionText: str, userAnswer: str = ""):
    """
    Use GPT-mini to explain a question in detail with structured output
    """
    prompt = f"""You are an expert interview coach. Explain this interview question in a structured, easy-to-understand format.

QUESTION: {questionText}

Provide your response as a JSON object with exactly these fields:
1. "context": A brief 2-3 sentence explanation of what this question tests and why it's important
2. "example": A single, complete example answer (not STAR format, just a natural paragraph showing how to answer well)
3. "focusAreas": An array of exactly 3 short, actionable tips (each 10-15 words max)

Example format:
{{
  "context": "This question assesses your ability to...",
  "example": "In my previous role, I faced a similar challenge when...",
  "focusAreas": [
    "Use specific examples from real experience",
    "Highlight the positive impact of your actions",
    "Keep your answer concise and structured"
  ]
}}

Provide ONLY the JSON object, no other text."""

    try:
        messages = [
            {"role": "system", "content": "You are a helpful interview coach who provides structured, JSON-formatted guidance."},
            {"role": "user", "content": prompt}
        ]
        
        resp = get_gpt_response(messages, model=None, max_tokens=600)
        if resp and 'choices' in resp:
            content = resp['choices'][0]['message']['content'].strip()
            
            # Try to parse JSON response
            try:
                # Remove markdown code blocks if present
                if content.startswith('```'):
                    content = content.split('```')[1]
                    if content.startswith('json'):
                        content = content[4:]
                
                import json
                parsed = json.loads(content)
                
                return {
                    "questionId": questionId,
                    "questionText": questionText,
                    "context": parsed.get("context", "This question tests your problem-solving and communication skills."),
                    "example": parsed.get("example", "Practice answering with specific examples from your experience."),
                    "focusAreas": parsed.get("focusAreas", [
                        "Be specific with real examples",
                        "Show positive outcomes",
                        "Structure your answer clearly"
                    ])[:3]  # Ensure exactly 3
                }
            except:
                # Fallback if JSON parsing fails
                pass
                
    except Exception as e:
        print(f"Teach me error: {e}")
    
    # Fallback response
    return {
        "questionId": questionId,
        "questionText": questionText,
        "context": "This question assesses your ability to handle challenges and demonstrate your problem-solving skills in real situations.",
        "example": "In my previous role, I encountered a similar situation where I analyzed the problem, developed a solution, implemented it successfully, and achieved positive results that improved team efficiency.",
        "focusAreas": [
            "Use specific examples from your experience",
            "Highlight measurable outcomes and impact",
            "Structure your answer clearly and concisely"
        ]
    }

def save_result(result: InterviewResult):
    """Save interview result to Firestore"""
    # Check if scores are all zero (indicates abandoned/empty session)
    if result.communicationScore == 0 and result.confidenceScore == 0 and result.relevanceScore == 0:
        return {"saved": False, "message": "Result discarded due to zero scores"}

    result.id = str(uuid.uuid4())
    
    # Convert Pydantic model to dict
    result_dict = result.model_dump()
    from google.cloud.firestore_v1 import SERVER_TIMESTAMP
    result_dict['createdAt'] = SERVER_TIMESTAMP
    
    # Save to Firestore
    firestore_client.collection('interview_results').document(result.id).set(result_dict)
    
    return result

def get_history(userId: str):
    """Get user's interview history from Firestore"""
    results = firestore_client.collection('interview_results')\
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
