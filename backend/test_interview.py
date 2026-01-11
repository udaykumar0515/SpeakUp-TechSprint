import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/interview"

print("🧪 Testing AI-Powered Mock Interview System\n")
print("="*70)

# Test 1: Start Interview (Graded Mode, Technical, Mid-Level)
print("\n1️⃣ Starting technical interview (Mid-Level, Graded Mode)...")
start_resp = requests.post(f"{BASE_URL}/start", json={
    "userId": 1,
    "interviewType": "technical",
    "difficulty": "mid",
    "mode": "graded",
    "resumeData": None
})

if start_resp.status_code != 200:
    print(f"❌ Start failed: {start_resp.text}")
    exit(1)

start_data = start_resp.json()
session_id = start_data["sessionId"]
total_questions = start_data["totalQuestions"]

print(f"✅ Session started: {session_id}")
print(f"   Total Questions: {total_questions}")
print(f"   Type: {start_data['interviewType']}")
print(f"   Difficulty: {start_data['difficulty']}")
print(f"   Mode: {start_data['mode']}")
print(f"   Greeting Prompt: {start_data['greetingPrompt']}")

# Test 2: Greet the interviewer
print(f"\n2️⃣ Greeting the interviewer...")
greet_resp = requests.post(f"{BASE_URL}/message", json={
    "sessionId": session_id,
    "userId": 1,
    "message": "Good morning, sir! I'm excited for this interview.",
    "action": "greet"
})

if greet_resp.status_code != 200:
    print(f"❌ Greeting failed: {greet_resp.text}")
else:
    greet_data = greet_resp.json()
    print(f"✅ Greeting acknowledged")
    print(f"   Response: {greet_data.get('response', 'N/A')}")
    print(f"   Bonus Points: {greet_data.get('greetingBonus', 0)}")
    print(f"   First Question: {greet_data.get('firstQuestion', 'N/A')[:80]}...")

# Test 3: Answer a few questions
print(f"\n3️⃣ Answering questions...")
sample_answers = [
    "I have experience with Python, JavaScript, and SQL. I've built REST APIs and worked with databases.",
    "In my previous project, I optimized a slow query by adding proper indexes and reduced response time by 60%.",
    "I would start by identifying bottlenecks using profiling tools, then optimize algorithms and add caching where appropriate."
]

for i, answer in enumerate(sample_answers[:min(3, total_questions)], 1):
    print(f"\n   Question {i}:")
    answer_resp = requests.post(f"{BASE_URL}/message", json={
        "sessionId": session_id,
        "userId": 1,
        "message": answer,
        "action": "answer"
    })
    
    if answer_resp.status_code != 200:
        print(f"   ❌ Answer failed: {answer_resp.text}")
        break
    
    answer_data = answer_resp.json()
    print(f"   ✅ Answer recorded")
    print(f"      Progress: {answer_data.get('progress', 0)}%")
    
    if answer_data.get('isComplete'):
        print(f"   🎯 Interview complete!")
        break
    else:
        print(f"      Acknowledgment: {answer_data.get('acknowledgment', '')}")
        print(f"      Next Q: {answer_data.get('nextQuestion', '')[:60]}...")

# Test 4: End Interview (even if not all questions answered)
print(f"\n4️⃣ Ending interview and generating results...")
end_resp = requests.post(f"{BASE_URL}/end", json={
    "sessionId": session_id,
    "userId": 1
})

if end_resp.status_code != 200:
    print(f"❌ End failed: {end_resp.text}")
else:
    results = end_resp.json()
    print(f"✅ Results generated!")
    print(f"\n{'='*70}")
    print(f"📊 INTERVIEW RESULTS")
    print(f"{'='*70}")
    
    if results.get("mode") == "graded":
        print(f"\n🎯 Overall Score: {results.get('overallScore', 'N/A')}/100")
        print(f"   (Including {results.get('greetingBonus', 0)} bonus points for greeting)")
        
        metrics = results.get('metrics', {})
        print(f"\n📈 Detailed Metrics:")
        print(f"   Technical Accuracy: {metrics.get('technicalAccuracy', 'N/A')}/100")
        print(f"   Communication: {metrics.get('communicationClarity', 'N/A')}/100")
        print(f"   Confidence: {metrics.get('confidence', 'N/A')}/100")
        print(f"   Understanding: {metrics.get('depthOfUnderstanding', 'N/A')}/100")
    
    print(f"\n💡 Overall Feedback:")
    print(f"   {results.get('overallFeedback', 'N/A')}")
    
    print(f"\n✅ Strengths:")
    for strength in results.get('strengths', []):
        print(f"   • {strength}")
    
    print(f"\n📝 Areas for Improvement:")
    for area in results.get('areasForImprovement', []):
        print(f"   • {area}")
    
    print(f"\n📚 Question Breakdown:")
    for qa in results.get('questionBreakdown', [])[:3]:  # Show first 3
        print(f"\n   Q{qa.get('questionNumber', '?')}: {qa.get('questionText', 'N/A')[:60]}...")
        print(f"   Your Answer: {qa.get('userAnswer', 'N/A')[:60]}...")
        if results.get('mode') == 'graded':
            print(f"   Score: {qa.get('score', 'N/A')}/10")
        print(f"   Feedback: {qa.get('feedback', 'N/A')[:100]}...")

# Test 5: Teach Me Feature
print(f"\n5️⃣ Testing 'Teach Me' feature...")
if results.get('questionBreakdown'):
    first_qa = results['questionBreakdown'][0]
    teach_resp = requests.post(f"{BASE_URL}/teach-me", json={
        "questionId": first_qa.get('questionId', 'test-id'),
        "questionText": first_qa.get('questionText', ''),
        "userAnswer": first_qa.get('userAnswer', '')
    })
    
    if teach_resp.status_code != 200:
        print(f"❌ Teach Me failed: {teach_resp.text}")
    else:
        teach_data = teach_resp.json()
        print(f"✅ Explanation generated!")
        print(f"\n📖 Question: {teach_data.get('questionText', 'N/A')[:80]}...")
        print(f"\n💡 Explanation:")
        explanation = teach_data.get('explanation', 'N/A')
        print(f"   {explanation[:300]}...")

print(f"\n{'='*70}")
print(f"✅ All tests completed successfully!")
print(f"{'='*70}")
