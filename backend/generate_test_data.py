"""
Test Data Generator - Populate Firestore with Mock Session Results

Creates fake data for testing the expanded metrics display:
- Aptitude test results with correct/incorrect breakdown
- Interview results with session metadata
- GD results with all 10 detailed metrics
- Resume analysis results

Usage:
    python generate_test_data.py YOUR_FIREBASE_UID

Replace YOUR_FIREBASE_UID with your actual Firebase UID from the database.
You can find it in Firestore Console or by logging in and checking the console.
"""

import sys
import uuid
from datetime import datetime, timedelta
import random

# Import Firebase admin
try:
    from firebase_config import firestore_client
    print("✅ Firebase client imported successfully")
except ImportError:
    print("❌ Could not import firebase_config. Make sure you're in the backend directory.")
    sys.exit(1)


def generate_aptitude_results(user_id: str, count: int = 5):
    """Generate fake aptitude test results"""
    topics = ["quantitative", "logical", "verbal"]
    results = []
    
    for i in range(count):
        topic = random.choice(topics)
        total_questions = random.choice([10, 15, 20])
        correct = random.randint(int(total_questions * 0.5), total_questions)
        incorrect = random.randint(0, total_questions - correct)
        unanswered = total_questions - correct - incorrect
        score = round((correct / total_questions) * 100)
        
        # Determine performance level
        if score >= 90:
            perf_level = "Excellent"
        elif score >= 75:
            perf_level = "Good"
        elif score >= 60:
            perf_level = "Average"
        else:
            perf_level = "Needs Improvement"
        
        result = {
            "id": str(uuid.uuid4()),
            "userId": user_id,
            "topic": topic,
            "score": score,
            "totalQuestions": total_questions,
            "accuracy": score,
            "timeTaken": random.randint(300, 1200),  # 5-20 minutes
            "correctAnswers": correct,
            "incorrectAnswers": incorrect,
            "unansweredQuestions": unanswered,
            "performanceLevel": perf_level,
            "createdAt": (datetime.now() - timedelta(days=i)).isoformat()
        }
        results.append(result)
    
    return results


def generate_interview_results(user_id: str, count: int = 4):
    """Generate fake interview results"""
    interview_types = ["Behavioral", "Technical", "HR Round", "Case Study"]
    job_roles = ["Software Engineer", "Data Scientist", "Product Manager", "Full Stack Developer"]
    
    results = []
    for i in range(count):
        comm_score = random.randint(65, 95)
        conf_score = random.randint(60, 90)
        rel_score = random.randint(70, 95)
        
        result = {
            "id": str(uuid.uuid4()),
            "userId": user_id,
            "communicationScore": comm_score,
            "confidenceScore": conf_score,
            "relevanceScore": rel_score,
            "feedback": f"Strong performance in {interview_types[i % len(interview_types)]}. "
                       f"Communication was clear and concise. "
                       f"Consider providing more specific examples in future interviews.",
            "interviewType": interview_types[i % len(interview_types)],
            "jobRole": job_roles[i % len(job_roles)],
            "questionCount": random.randint(5, 10),
            "sessionDuration": random.randint(15, 45),
            "createdAt": (datetime.now() - timedelta(days=i * 2)).isoformat()
        }
        results.append(result)
    
    return results


def generate_gd_results(user_id: str, count: int = 3):
    """Generate fake GD results with all 10 detailed metrics"""
    topics = [
        "Impact of AI on Employment",
        "Climate Change Solutions",
        "Future of Remote Work",
        "Social Media Influence",
        "Education System Reform"
    ]
    
    results = []
    for i in range(count):
        # Generate scores
        verbal = random.randint(70, 95)
        confidence = random.randint(65, 90)
        interactivity = random.randint(75, 95)
        argument = random.randint(70, 90)
        relevance = random.randint(75, 95)
        leadership = random.randint(60, 85)
        
        overall = round((verbal + confidence + interactivity + argument + relevance + leadership) / 6)
        
        # Apply pause penalty
        pause_count = random.randint(0, 3)
        pause_penalty = pause_count * 2
        overall = max(0, overall - pause_penalty)
        
        strengths = random.sample([
            "Clear articulation",
            "Strong arguments",
            "Active listening",
            "Good examples provided",
            "Respectful of others' views",
            "Logical reasoning"
        ], k=3)
        
        improvements = random.sample([
            "Provide more data-backed points",
            "Reduce interruptions",
            "Maintain better eye contact",
            "Speak more concisely",
            "Include diverse perspectives"
        ], k=2)
        
        result = {
            "id": str(uuid.uuid4()),
            "userId": user_id,
            "topic": topics[i % len(topics)],
            "duration": 15,
            "score": overall,
            "verbalAbility": verbal,
            "confidence": confidence,
            "interactivity": interactivity,
            "argumentQuality": argument,
            "topicRelevance": relevance,
            "leadership": leadership,
            "strengths": strengths,
            "improvements": improvements,
            "pauseCount": pause_count,
            "pausePenalty": pause_penalty,
            "createdAt": (datetime.now() - timedelta(days=i * 3)).isoformat()
        }
        results.append(result)
    
    return results


def generate_resume_results(user_id: str, count: int = 2):
    """Generate fake resume analysis results"""
    results = []
    filenames = [
        "John_Doe_Resume_2024.pdf",
        "Updated_Resume_Jan2024.pdf"
    ]
    
    for i in range(count):
        ats_score = random.randint(70, 95)
        
        suggestions = random.sample([
            "Add more quantifiable achievements (e.g., 'Increased sales by 30%')",
            "Include relevant industry keywords for ATS optimization",
            "Improve formatting consistency throughout the document",
            "Add a professional summary at the top",
            "Quantify your impact in each role",
            "Include relevant certifications and skills",
            "Use action verbs to start bullet points",
            "Tailor resume to specific job descriptions"
        ], k=random.randint(4, 6))
        
        result = {
            "id": str(uuid.uuid4()),
            "userId": user_id,
            "atsScore": ats_score,
            "suggestions": suggestions,
            "fileName": filenames[i % len(filenames)],
            "createdAt": (datetime.now() - timedelta(days=i * 7)).isoformat()
        }
        results.append(result)
    
    return results


def populate_firestore(user_id: str):
    """Populate Firestore with all test data"""
    print(f"\n🔄 Generating test data for user: {user_id}\n")
    
    # Generate data
    aptitude_results = generate_aptitude_results(user_id, 5)
    interview_results = generate_interview_results(user_id, 4)
    gd_results = generate_gd_results(user_id, 3)
    resume_results = generate_resume_results(user_id, 2)
    
    # Save to Firestore
    try:
        # Aptitude results
        print(f"📊 Saving {len(aptitude_results)} aptitude results...")
        for result in aptitude_results:
            firestore_client.collection('aptitude_results').document(result['id']).set(result)
        print(f"   ✅ Saved {len(aptitude_results)} aptitude results")
        
        # Interview results
        print(f"🎤 Saving {len(interview_results)} interview results...")
        for result in interview_results:
            firestore_client.collection('interview_results').document(result['id']).set(result)
        print(f"   ✅ Saved {len(interview_results)} interview results")
        
        # GD results
        print(f"💬 Saving {len(gd_results)} GD results...")
        for result in gd_results:
            firestore_client.collection('gd_results').document(result['id']).set(result)
        print(f"   ✅ Saved {len(gd_results)} GD results")
        
        # Resume results
        print(f"📄 Saving {len(resume_results)} resume results...")
        for result in resume_results:
            firestore_client.collection('resume_results').document(result['id']).set(result)
        print(f"   ✅ Saved {len(resume_results)} resume results")
        
        print(f"\n✅ Successfully generated test data!")
        print(f"\n📈 Summary:")
        print(f"   - {len(aptitude_results)} Aptitude Tests")
        print(f"   - {len(interview_results)} Interview Sessions")
        print(f"   - {len(gd_results)} Group Discussions")
        print(f"   - {len(resume_results)} Resume Analyses")
        print(f"\n🎯 Go to your Profile page to see the results!")
        
    except Exception as e:
        print(f"\n❌ Error saving to Firestore: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\n❌ Usage: python generate_test_data.py YOUR_FIREBASE_UID")
        print("\nExample:")
        print("   python generate_test_data.py LtCZ70rv8eNOcKbLjkiSNWeFWKC3")
        print("\nYou can find your Firebase UID by:")
        print("   1. Log into the app")
        print("   2. Open browser console")
        print("   3. Check the network tab for any API call")
        print("   4. Your UID will be in the URL (something like 'LtCZ70rv...')")
        sys.exit(1)
    
    user_id = sys.argv[1]
    populate_firestore(user_id)
