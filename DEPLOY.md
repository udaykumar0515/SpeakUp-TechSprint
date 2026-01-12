# Deployment Guide for SpeakUp

This guide explains how to deploy the SpeakUp application, which consists of a Python FastAPI backend and a React/Vite frontend.

## 1. Backend Deployment (Render / Railway)

We recommend **Render** or **Railway** for the backend.

### Steps for Render:

1.  Create a new **Web Service** on Render.
2.  Connect your GitHub repository.
3.  **Settings:**
    - **Root Directory:** `backend`
    - **Runtime:** Python 3
    - **Build Command:** `pip install -r requirements.txt`
    - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables:**
    To make the app work, you must set these environment variables in the Render dashboard:
    - `GEMINI_API_KEY`: Your Google Gemini API Key.
    - `FIREBASE_SERVICE_ACCOUNT_JSON`: **IMPORTANT!** Open your local `backend/firebase-service-account.json` file, copy all the JSON content, and paste it as the value for this variable. This allows the backend to authenticate with Firebase without checking the sensitive file into Git.
    - Any other variables from your `backend/.env` file.

## 2. Frontend Deployment (Vercel / Netlify)

We recommend **Vercel** or **Netlify** for the frontend.

### Steps for Vercel:

1.  Create a new **Project** on Vercel.
2.  Connect your GitHub repository.
3.  **Settings:**
    - **Root Directory:** `SpeakUp-Frontend`
    - **Framework Preset:** Vite
    - **Build Command:** `npm run build` (or `npm install && npm run build`)
    - **Output Directory:** `dist`
4.  **Environment Variables:**
    - `VITE_API_BASE_URL`: The URL of your deployed Backend (e.g., `https://speakup-backend.onrender.com`). **Do not add a trailing slash** (unless your code handles it, but currently it expects base URL).
    - `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, etc.: Add all your Firebase client-side config variables here if they are not hardcoded.

---

## 3. Troubleshooting

### Backend: "resolution-too-deep" Error

**Problem:** Pip cannot resolve dependencies during build.

**Solution:** This has been fixed in the updated `requirements.txt` with pinned versions. If you still see this error:

1. Make sure you've pushed the latest `requirements.txt` to GitHub
2. Trigger a new deploy on Render (Manual Deploy → Clear build cache & deploy)

### Backend: Firebase Authentication Errors

**Problem:** "Firebase service account file not found" or authentication failures.

**Solution:**

1. Ensure `FIREBASE_SERVICE_ACCOUNT_JSON` is set correctly in Render environment variables
2. The value should be the **entire JSON content** from your local `backend/firebase-service-account.json` file
3. Make sure there are no extra spaces or formatting issues when pasting the JSON

### Frontend: API Connection Errors

**Problem:** Frontend cannot connect to backend API.

**Solution:**

1. Check that `VITE_API_BASE_URL` is set in Vercel environment variables
2. The URL should be your Render backend URL (e.g., `https://your-app.onrender.com`)
3. **No trailing slash** in the URL
4. After changing env vars, you may need to redeploy the frontend

### Backend: Document AI Errors

**Problem:** Resume analysis fails with "Document AI not configured".

**Solution:**

1. Set `DOCUMENTAI_PROJECT_ID`, `DOCUMENTAI_LOCATION`, and `DOCUMENTAI_PROCESSOR_ID` in Render
2. The app will use `FIREBASE_SERVICE_ACCOUNT_JSON` for Document AI credentials automatically
3. If you have a separate Google Cloud service account, set `GOOGLE_APPLICATION_CREDENTIALS` as JSON string

---

## Summary

- **Backend**: Runs on Render/Railway. Listens on `$PORT`. Configured via `FIREBASE_SERVICE_ACCOUNT_JSON`.
- **Frontend**: Hosted on Vercel/Netlify. Connects to Backend via `VITE_API_BASE_URL`.
