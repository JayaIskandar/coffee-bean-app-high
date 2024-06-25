import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin.auth import InvalidIdTokenError
import os
import json

# Function to construct Firebase credentials from environment variables
def get_firebase_credentials_from_env():
    private_key = os.getenv("FIREBASE_PRIVATE_KEY")
    if private_key is None:
        raise ValueError("FIREBASE_PRIVATE_KEY environment variable is not set.")
    
    print("Loaded FIREBASE_PRIVATE_KEY:", private_key)  # Debug print
    
    return {
        "type": os.getenv("FIREBASE_TYPE", "service_account"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": private_key.replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
    }

# Global Firestore client
db = None
firebase_initialized = False  # Flag to track if Firebase is already initialized

def initialize_firebase():
    global db, firebase_initialized
    
    if not firebase_initialized:
        try:
            # Try to get the default app, if it exists
            firebase_admin.get_app()
        except ValueError:
            # If the default app doesn't exist, initialize it using credentials from environment variables
            firebase_credentials = get_firebase_credentials_from_env()
            cred = credentials.Certificate(firebase_credentials)
            
            firebase_admin.initialize_app(cred)
        
        # Initialize Firestore
        db = firestore.client()
        firebase_initialized = True  # Mark Firebase as initialized
        print("Firebase initialized successfully.")
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
        global db
        
        if db is None:
            initialize_firebase()  # Initialize Firebase if not already initialized
        
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
        global db
        
        if db is None:
            initialize_firebase()  # Initialize Firebase if not already initialized
        
        user = auth.get_user_by_email(email)
        if user:
            # Implement password verification logic here
            return user
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None

# Call initialize_firebase() once at the start of your application
initialize_firebase()
