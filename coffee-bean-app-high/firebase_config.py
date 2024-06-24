import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def initialize_firebase():
    # Check if the app is already initialized
    if not firebase_admin._apps:
        # Load Firebase credentials from environment variables or configuration files
        firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if firebase_credentials_path:
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred)
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

def send_verification_email(user):
    try:
        auth.send_email_verification(user.uid)
        print("Verification email sent.")
    except Exception as e:
        print(f"Error sending verification email: {e}")

def create_user_with_email_password(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        send_verification_email(user)
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
