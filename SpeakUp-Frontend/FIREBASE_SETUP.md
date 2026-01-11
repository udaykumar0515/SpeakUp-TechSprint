# Firebase Integration Instructions for SpeakUp

This document explains how to connect Firebase to the main project when you're ready.

## Prerequisites

1.  A Firebase project from the [Firebase Console](https://console.firebase.google.com/).
2.  A Web App created within that project.
3.  Authentication enabled (Email/Password method).

## Step 1: Add API Keys

Create a `.env` file in the root directory with the following environment variables:

```env
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_APP_ID=your-app-id
VITE_FIREBASE_API_KEY=your-api-key
```

## Step 2: Enable Firebase in the Code

To switch from mock authentication to real Firebase authentication, follow these steps:

### 1. Update `client/src/hooks/use-auth.tsx`

The file currently uses mock logic. To enable Firebase, you need to uncomment the Firebase logic and comment out the mock logic.

**Current Mock Login:**

```typescript
const login = async (email: string, password: string) => {
  setIsLoading(true);
  await new Promise((resolve) => setTimeout(resolve, 800));
  // ... mock user setup ...
  setUser(mockUser);
  setIsLoading(false);
  setLocation("/dashboard");
};
```

**Replace with Firebase Login:**

```typescript
const login = async (email: string, password: string) => {
  try {
    setIsLoading(true);
    await signInWithEmailAndPassword(auth, email, password);
    setLocation("/dashboard");
  } catch (error: any) {
    toast({
      title: "Login failed",
      description: error.message,
      variant: "destructive",
    });
  } finally {
    setIsLoading(false);
  }
};
```

### 2. Update `client/src/lib/firebase.ts`

Ensure this file is correctly pointing to your environment variables:

```typescript
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: `${import.meta.env.VITE_FIREBASE_PROJECT_ID}.firebaseapp.com`,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};
```

## Step 3: Deployment

After deployment, remember to add your production domain to the **Authorized Domains** list in the Firebase Authentication settings.
