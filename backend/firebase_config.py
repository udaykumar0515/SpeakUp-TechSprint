import os
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
        print("✅ Firebase already initialized")
    except ValueError:
        # Path to service account key
        service_account_path = os.path.join(
            os.path.dirname(__file__), 
            "firebase-service-account.json"
        )
        
        if not os.path.exists(service_account_path):
            raise FileNotFoundError(
                f"Firebase service account file not found at: {service_account_path}"
            )
        
        # Initialize with service account
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized successfully")

# Initialize on module import
initialize_firebase()

# Export Firebase clients
auth_client = auth
firestore_client = firestore.client()

def verify_firebase_token(id_token: str):
    """
    Verify Firebase ID token and return decoded token
    
    Args:
        id_token: Firebase ID token from Authorization header
        
    Returns:
        dict: Decoded token with uid, email, etc.
        
    Raises:
        Exception: If token is invalid
    """
    try:
        decoded_token = auth_client.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise Exception(f"Invalid token: {str(e)}")

def get_or_create_user(uid: str, email: str, name: str = None):
    """
    Get or create user document in Firestore
    
    Args:
        uid: Firebase user ID
        email: User email
        name: User display name
        
    Returns:
        dict: User document
    """
    user_ref = firestore_client.collection('users').document(uid)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        return user_doc.to_dict()
    else:
        # Create new user document
        user_data = {
            'uid': uid,
            'email': email,
            'name': name or email.split('@')[0],
            'createdAt': firestore.SERVER_TIMESTAMP,
            'age': None,
            'gender': None,
            'occupation': None,
            'avatarUrl': None
        }
        user_ref.set(user_data)
        return user_data
