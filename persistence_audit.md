# SpeakUp Persistence Audit Report

## 1. Executive Summary

**Project Status:**
The SpeakUp project is currently **100% stateless**. All data—including user profiles, interview sessions, group discussion logs, and results—is stored in Python in-memory dictionaries and lists. This means **all data is lost when the backend server restarts**.

**Goal:**
To integrate Firebase to provide permanent data storage, authentication, and history tracking.

**Key Findings:**

- **Zero Persistence:** No database is currently connected.
- **In-Memory dependency:** 5 key services (`auth`, `interview`, `gd`, `aptitude`, `resume`) rely on global variables for storage.
- **Frontend Readiness:** The frontend already has hooks (`useCreate...Result`) structured to save data, but the backend implementation is transient.
- **Critical Gaps:** Session state (active interviews/GDs) is also in-memory. If a server restarts mid-session, the user loses progress.

---

## 2. Feature Analysis: Current vs. Ideal State

| Feature                     | Currently Persisted? | Current Storage                        | Ideal Storage                                 |
| :-------------------------- | :------------------: | :------------------------------------- | :-------------------------------------------- |
| **User Profiles**           |        ❌ No         | `auth_service.USERS` (Dict)            | **Firebase Auth** + `users` collection        |
| **Mock Interview Sessions** |        ❌ No         | `interview_service.INTERVIEW_SESSIONS` | **Firestore** `interviews` (active sessions)  |
| **Interview Results**       |        ❌ No         | `interview_service.INTERVIEW_RESULTS`  | **Firestore** `interview_results` (completed) |
| **GD Sessions**             |        ❌ No         | `gd_service.GD_SESSIONS`               | **Firestore** `gd_sessions` (active)          |
| **GD Results**              |        ❌ No         | `gd_service.GD_RESULTS`                | **Firestore** `gd_results` (completed)        |
| **Aptitude Results**        |        ❌ No         | `aptitude_service.APTITUDE_RESULTS`    | **Firestore** `aptitude_results`              |
| **Resume Analysis**         |        ❌ No         | `resume_service.RESUME_RESULTS`        | **Firestore** `resume_results`                |
| **Dashboard Stats**         |        ❌ No         | Calculated on-the-fly from lists       | Calculated from Firestore queries             |

---

## 3. Data Model Definitions

The following data models need to be migrated from Pydantic in-memory models to Firestore documents.

### User Profile

```json
// Collection: users
// Doc ID: <firebase_uid>
{
  "email": "user@example.com",
  "name": "Jane Doe",
  "photoURL": "https://...",
  "createdAt": "ISO8601 Timestamp",
  "metadata": {
    "occupation": "Student",
    "gender": "Female",
    "age": 22
  }
}
```

### Interview Result

```json
// Collection: interview_results
// Doc ID: <auto-id>
{
  "userId": "<firebase_uid>",
  "interviewType": "technical", // or "hr", "behavioral"
  "difficulty": "medium",
  "score": 85,
  "feedback": "Good structured answers...",
  "metrics": {
    "communication": 80,
    "technical": 90,
    "confidence": 85
  },
  "transcript": [
    { "role": "ai", "content": "Question..." },
    { "role": "user", "content": "Answer..." }
  ],
  "createdAt": "Timestamp"
}
```

### GD Result

```json
// Collection: gd_results
// Doc ID: <auto-id>
{
  "userId": "<firebase_uid>",
  "topic": "Impact of AI",
  "duration": 600, // seconds
  "score": 78,
  "feedback": "Great leadership shown...",
  "metrics": {
    "speakingTime": 120,
    "interruptions": 2,
    "leadershipScore": 8
  },
  "createdAt": "Timestamp"
}
```

### Aptitude Result

```json
// Collection: aptitude_results
// Doc ID: <auto-id>
{
  "userId": "<firebase_uid>",
  "topic": "Quantitative",
  "score": 90, // percentage
  "totalQuestions": 10,
  "correctAnswers": 9,
  "timeTaken": 150, // seconds
  "createdAt": "Timestamp"
}
```

### Resume Analysis

```json
// Collection: resume_results
// Doc ID: <auto-id>
{
  "userId": "<firebase_uid>",
  "fileName": "resume.pdf",
  "atsScore": 75,
  "parsedData": {
    "skills": ["Python", "React"],
    "experience": "..."
  },
  "suggestions": ["Add more keywords", "Fix formatting"],
  "createdAt": "Timestamp"
}
```

---

## 4. Frontend & API Gap Analysis

### Dashboard (`Dashboard.tsx`)

- **Current Behavior:** Calls `/api/dashboard/stats/{userId}`.
- **Backend Logic:** Aggregates counts/averages from 4 separate in-memory lists.
- **Firebase Impact:** This is expensive in NoSQL.
- **Recommendation:**
  1.  **Option A (Simpler):** Run 4 separate queries (`count` queries) on the client or backend.
  2.  **Option B (Scalable):** Maintain a `stats` subcollection or field on the User document that increments counters when new results are saved.

### History Screens (`Profile.tsx`, History tabs)

- **Current Behavior:** Calls `/api/{feature}/history/{userId}`.
- **Backend Logic:** Filters the global list by `userId`.
- **Firebase Impact:** straightforward integration. Replace list comprehension with `.where("userId", "==", uid)` queries.

### Active Sessions (Interview/GD)

- **Current Behavior:** Frontend stores `sessionId` and polls/pushes to backend. State is held in backend memory (`INTERVIEW_SESSIONS[sessionId]`).
- **Risk:** If backend restarts, connection is lost.
- **Recommendation:**
  - **Phase 1:** Keep session state in-memory (Acceptable for MVP). Only save _final results_ to Firebase.
  - **Phase 2:** Persist active session state to Firestore to allow resuming (e.g., if page refresh happens).

---

## 5. Suggested Firestore Schema

```text
/users/{userId}
    - email: string
    - name: string
    - ...

/interview_results/{resultId}
    - userId: string
    - score: number
    - ... (see model above)

/gd_results/{resultId}
    - userId: string
    - score: number
    - ...

/aptitude_results/{resultId}
    - userId: string
    - score: number
    - ...

/resume_results/{resultId}
    - userId: string
    - score: number
    - ...
```

---

## 6. Implementation Roadmap

1.  **Setup Firebase Admin SDK** in Backend (`backend/config/firebase.py`).
2.  **Replace Auth Service:** verify Firebase tokens instead of mock login.
3.  **Update Services:**
    - Modify `save_result` functions in all 4 services to write to Firestore.
    - Modify `get_history` functions to query Firestore.
    - Update `dashboard_service` to query Firestore (or calculate from history).
4.  **Frontend Auth:** Integrate `firebase/auth` on client side to get real tokens.

**Summary:** The project architecture is clean and service-oriented, which makes swapping the "in-memory mock database" with Firestore relatively straightforward. The main complexity will be rewriting the `dashboard_service` to efficiently aggregate statistics from Firestore.
