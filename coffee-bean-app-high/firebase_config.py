import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

# Global Firestore client
db = None

def initialize_firebase():
    global db
    # Check if the app is already initialized
    if not firebase_admin._apps:
        # Load Firebase credentials from environment variables or configuration files
        firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if firebase_credentials_path:
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred)
            # Initialize Firestore
            db = firestore.client()
        else:
            raise ValueError("Firebase credentials path not provided.")
    else:
        print("Firebase app already initialized.")

def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying ID token: {e}")
        return None

def create_user_with_email_password(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        # Store user details in Firestore (including createdAt timestamp if not set)
        user_ref = db.collection("users").document(user.uid)
        user_data = {
            "email": email,
            "uid": user.uid,
        }
        # Check if 'createdAt' field exists, and set it only if it doesn't
        if "createdAt" not in user_data:
            user_data["createdAt"] = firestore.SERVER_TIMESTAMP
        
        user_ref.set(user_data, merge=True)  # Merge with existing data if any
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

# Conditionally load environment variables from .env file only in local development
if os.getenv('ENVIRONMENT') == 'development':
    from dotenv import load_dotenv
    load_dotenv()
