# SpeakUp - AI-Powered Placement Prep Platform 🚀

**SpeakUp** is a comprehensive, AI-driven platform designed to supercharge your placement preparation. Whether you're preparing for aptitude tests, technical interviews, or group discussions, SpeakUp provides a realistic, interactive, and personalized environment to practice and improve.

<div align="center">
  <img src="client/public/vite.svg" alt="SpeakUp Logo" width="100" />
</div>

---

## 🌟 Key Features

### 1. 📊 Interactive Dashboard

Your central command center for preparation.

- **Personalized Greeting**: Welcomes you back and keeps you motivated.
- **Smart Stats**: Track your progress with detailed metrics on total sessions, average scores, and activity trends.
- **Quick Access**: Instantly jump into any practice module (Aptitude, Interview, GD, Resume) with beautiful, animated cards.
- **Recent Activity**: A timeline of your past sessions with scores and performance indicators to help you stay consistent.

### 2. 🧠 Aptitude Practice Arena

Sharpen your cognitive skills with diverse testing modes.

- **3 Core Topics**: Quantitative Aptitude, Logical Reasoning, and Verbal Ability.
- **⚡ AI-Powered Challenge Mode**: A special "Hard Questions" mode that generates **3 random, high-difficulty questions** to test your limits. Perfect for quick, intense practice.
- **Regular Practice**: Customize your test with **10 to 30 questions** based on your time and preference.
- **Detailed Results**:
  - **Score Analysis**: Comprehensive performance level (Excellent/Good/Needs Improvement).
  - **Review Mode**: Go through every question with detailed **correct/incorrect indicators** and **explanations**.
  - **Visuals**: Circular progress charts to visualize your score.

### 3. 💼 AI Mock Interviewer

Experience realistic interview scenarios without the pressure.

- **Flexible Setup**: Choose your **Interview Type** (HR/Technical), **Difficulty** (Easy/Medium/Hard), and **Mode** (Practice vs. Graded).
- **Realistic Flow**:
  - **Greeting Phase**: The session starts only when you professionally greet the interviewer (or auto-starts after 15s).
  - **AI Chat Interface**: A dynamic, conversational interface where the AI asks relevant questions based on your responses.
  - **Resume & Non-Resume Modes**: Capable of tailoring questions based on your profile (if configured) or general topics.
- **Instant Feeback**: Get a detailed report on your answers, highlighting strengths and areas for improvement.

### 4. 🗣️ Group Discussion (GD) Simulator

A unique feature to practice participating in group discussions with AI bots.

- **Smart Bots**: Interact with AI participants who have distinct personalities and roles.
- **Preparation Phase**: Get 60 seconds to gather your thoughts on the topic before the discussion begins.
- **Dynamic Topics**: Choose from trending topics (e.g., "AI Impact", "Work from Home") or let the AI pick a random one.
- **Real-time Metrics**:
  - **Share of Voice**: Live tracking of how much you speak vs. the bots to ensure balanced participation.
  - **Speaking Tips**: Context-aware advice displayed during the session.
  - **Pause Penalties**: Pausing the session is allowed but discourages, affecting your final "Discipline" score.
- **Comprehensive Analysis**:
  - Scores on 6 parameters: **Verbal Ability, Confidence, Interactivity, Argument Quality, Topic Relevance, and Leadership**.
  - **Detailed Feedback**: AI generates a full performance report with actionable advice.

### 5. 📄 Smart Resume Analyzer

Optimize your resume for Applicant Tracking Systems (ATS).

- **ATS Compatibility Score**: Upload your PDF resume and get an instant score (0-100).
- **Information Extraction**: Automatically parses Skills, Education, and Experience to show you what recruiters see.
- **Actionable Suggestions**: Specific tips on how to improve your resume's formatting, keywords, and content.
- **Drag & Drop Interface**: Simple, user-friendly upload zone.

---

## 🛠️ Technology Stack

### Frontend

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + Shadcn UI
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Routing**: Wouter

### Backend

- **API Framework**: FastAPI (Python)
- **Authentication**: Firebase Authentication
- **Database**: Cloud Firestore (NoSQL)

### AI & ML (100% Google Technologies)

- **LLM**: Google Gemini API (2.0 Flash & 1.5 Pro)
- **OCR**: Google Document AI
- **Deployment**: Firebase Hosting / Google Cloud Run

**🎯 Built for Google TechSprint Hackathon**

## 🚀 Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.9+)

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/udaykumar0515/speakup.git
    cd speakup
    ```

2.  **Frontend Setup**

    ```bash
    cd SpeakUp-Frontend
    npm install
    npm run dev
    ```

3.  **Backend Setup**

    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```

4.  **Open the App**
    Visit `http://localhost:5173` in your browser.

---

<center>Made with ❤️ for Students & Job Seekers</center>
