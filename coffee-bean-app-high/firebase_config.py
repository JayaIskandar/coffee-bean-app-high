import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin.auth import InvalidIdTokenError
import os
import json

# Explicitly load the .env file if running locally
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
    print("Loaded .env file")

# Print the environment variables for debugging purposes
print("ENVIRONMENT:", os.getenv('ENVIRONMENT'))
print("FIREBASE_CREDENTIALS_PATH:", os.getenv('FIREBASE_CREDENTIALS_PATH'))

# Global Firestore client
db = None
firebase_initialized = False  # Flag to track if Firebase is already initialized

def initialize_firebase():
    global db, firebase_initialized
    
    if not firebase_initialized:
        # Load Firebase credentials from environment variables or configuration files
        firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if firebase_credentials_path:
            try:
                # Try to load the credentials as a JSON string
                credentials_json = json.loads(firebase_credentials_path)
                cred = credentials.Certificate(credentials_json)
            except json.JSONDecodeError:
                # Fallback: assume it is a file path
                cred = credentials.Certificate(firebase_credentials_path)
                
            firebase_admin.initialize_app(cred)
            # Initialize Firestore
            db = firestore.client()
            firebase_initialized = True  # Mark Firebase as initialized
        else:
            raise ValueError("Firebase credentials path not provided.")
    else:
        print("Firebase app already initialized.")

def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except InvalidIdTokenError as e:
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

def verify_user_with_email_password(email, password):
    try:
        user = auth.get_user_by_email(email)
        if user:
            # Implement password verification logic here
            return user
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None

# Call initialize_firebase() once at the start of your application
initialize_firebase()
