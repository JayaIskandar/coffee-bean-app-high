import streamlit as st
import os
from streamlit_option_menu import option_menu
from firebase_config import initialize_firebase, create_user_with_email_password, verify_user_with_email_password, db

# IMPORT LIBRARIES FOR GOOGLE AUTHENTICATION
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
from firebase_admin import auth, firestore
import json

import webbrowser

# Explicitly load the .env file if running locally
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Initialize Firebase SDK
initialize_firebase()

# Determine the environment based on the URL
base_url = os.getenv("BASE_URL_DEV") if os.getenv("ENVIRONMENT") == 'development' else os.getenv("BASE_URL_PROD")

# Define base directory where HTML files are located
base_dir = os.path.abspath(os.path.dirname(__file__))


##################### TO MAKE FULL WIDTH  #####################
# Set page config once at the very beginning
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
##################### TO MAKE FULL WIDTH  #####################


# FUNCTION FOR LANDING PAGE (BEFORE AUTHENTICATED)
def show_landing_page():
    # Remove default Streamlit styling
    st.markdown("""
        <style>
            #root > div:nth-child(1) > div > div > div > div > section > div {
                padding-top: 0;
            }
            .reportview-container {
                margin-top: -2em;
            }
            #MainMenu {visibility: hidden;}
            .stDeployButton {display:none;}
            footer {visibility: hidden;}
            #stDecoration {display:none;}
        </style>
    """, unsafe_allow_html=True)

    # Use a div wrapper for the landing page content
    #st.markdown('<div class="landing-page">', unsafe_allow_html=True)
    

    
    landing_html_path = os.path.join(base_dir, 'landing.html')
    with open(landing_html_path, 'r', encoding='utf-8') as file:
        landing_html = file.read()
    
    st.html(landing_html)
    #st.markdown('<div class="custom-card">', unsafe_allow_html=True)

# FUNCTION FOR LANDING PAGE (BEFORE AUTHENTICATED)    

########################################################################


def exchange_code_for_token(code):
    
    # Ensure Firebase is initialized
    if db is None:
        initialize_firebase()
        
    # Set up the OAuth 2.0 flow using environment variables and base_url
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=base_url
    )
    
    # Exchange the authorization code for credentials
    flow.fetch_token(code=code)
    
    # Get the ID token from the credentials
    id_info = id_token.verify_oauth2_token(
        flow.credentials.id_token, requests.Request(), os.getenv("GOOGLE_CLIENT_ID"),
        clock_skew_in_seconds=10  # Allow a 10-second clock skew
    )
    
    # Check if the token is valid
    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Wrong issuer.')
    
    # Get or create the Firebase user
    try:
        firebase_user = auth.get_user_by_email(id_info['email'])
    except auth.UserNotFoundError:
        firebase_user = auth.create_user(
            email=id_info['email'],
            display_name=id_info.get('name'),
            photo_url=id_info.get('picture')
        )
    
    # Store user details in Firestore
    user_ref = db.collection("users").document(firebase_user.uid)
    user_data = {
        "email": firebase_user.email,
        "uid": firebase_user.uid,
        "display_name": firebase_user.display_name,
        "photo_url": firebase_user.photo_url,
        "createdAt": firestore.SERVER_TIMESTAMP  # Add the createdAt timestamp
    }
    
    user_ref.set(user_data, merge=True)  # Merge with existing data if any
    
    # Update session state
    st.session_state["user_id"] = firebase_user.uid
    st.session_state["authenticated"] = True
    
    print(f"User UID set in exchange_code_for_token: {firebase_user.uid}")
    
    # Set the session state here
    st.session_state["user"] = firebase_user.uid
    st.session_state["authenticated"] = True
    
    return {
        "uid": firebase_user.uid,
        "email": firebase_user.email,
        "createdAt": firestore.SERVER_TIMESTAMP
    }


    
    
def show_sign_in_page():
    st.title("Sign In")
    
    # Email input
    email = st.text_input("Email")
    # Password input
    password = st.text_input("Password", type="password")
    
    # Sign In button for Email/Password
    if st.button("Sign In"):
        user = verify_user_with_email_password(email, password)
        if user:
            st.session_state["user_id"] = user.uid  # Store user ID in session state
            st.session_state["authenticated"] = True
            # Update URL to remove any previous query parameters and set authenticated to true
            st.query_params.clear()
            st.query_params["authenticated"] = "true"
            st.rerun()
        else:
            st.error("Failed to sign in. Please check your credentials and try again.")
    
    # Horizontal line with spacing
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    
    # OR text
    st.markdown("<h5 style='text-align: center;'>OR</h5>", unsafe_allow_html=True)
    
    # Google sign-in section
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")  # Retrieve Google Client ID from environment variable
    
    if google_client_id:
        sign_in_url = f"https://accounts.google.com/o/oauth2/auth?client_id={google_client_id}&redirect_uri={base_url}&response_type=code&scope=openid%20email%20profile&access_type=offline"
        
        # Center the Google sign-in button
        st.markdown(f'<div style="text-align: center;">'
                    f'<a href="{sign_in_url}" style="display: inline-block; padding: 10px 20px; color: white; background-color: #4285F4; border-radius: 5px; text-decoration: none; margin-top: 20px; margin-right:20px; font-weight: bold;">'
                    f'<img src="https://raw.githubusercontent.com/JayaIskandar/beanxpert-stock-img/main/icons8-google-48.png" style="vertical-align: middle; margin-right: 8px;" width="24" height="24">'
                    f'Sign in with Google</a></div>', unsafe_allow_html=True)
        
        # Check if the user has returned from Google authentication
        code = st.query_params.get("code")
        user_info = None  # Initialize user_info with a default value
        if code:
            try:
                # Exchange the code for a token and get user info
                user_info = exchange_code_for_token(code)
                if user_info and user_info.get("success"):
                    # Session state is already set in exchange_code_for_token
                    print(f"User UID stored in session state (Google): {st.session_state['user']}")  # Debug print
                    st.query_params.clear()
                    st.query_params(authenticated="true")
                    st.rerun()
                else:
                    st.error("Failed to get user information from Google sign-in")
            except Exception as e:
                st.error(f"Failed to authenticate with Google: {str(e)}")
        
        # Add this debug print at the end of the function
        if "user" in st.session_state:
            print(f"Current user in session state: {st.session_state['user']}")
            if user_info:  # Check if user_info is not None before accessing it
                st.write(f"Logged in as: {user_info['email']}")
        else:
            print("No user in session state")
    else:
        st.error("Google Client ID not found. Please set the GOOGLE_CLIENT_ID environment variable.")

        
def show_register_page():
    st.title("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password == confirm_password: 
            user = create_user_with_email_password(email, password)
            if user:
                st.success("Account created. Please proceed to sign-in!")
            else:
                st.error("Failed to create user. Please try again.")

   
    # Horizontal line with spacing
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    
    # OR text
    st.markdown("<h5 style='text-align: center;'>OR</h5>", unsafe_allow_html=True)
    
    # Google sign-in section
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")  # Retrieve Google Client ID from environment variable
    
    if google_client_id:
        sign_in_url = f"https://accounts.google.com/o/oauth2/auth?client_id={google_client_id}&redirect_uri={base_url}&response_type=code&scope=openid%20email%20profile&access_type=offline"
        
        # Center the Google sign-in button
        st.markdown(f'<div style="text-align: center;">'
                    f'<a href="{sign_in_url}" style="display: inline-block; padding: 10px 20px; color: white; background-color: #4285F4; border-radius: 5px; text-decoration: none; margin-top: 20px; margin-right:20px; font-weight: bold;">'
                    f'<img src="https://raw.githubusercontent.com/JayaIskandar/beanxpert-stock-img/main/icons8-google-48.png" style="vertical-align: middle; margin-right: 8px;" width="24" height="24">'
                    f'Sign up with Google</a></div>', unsafe_allow_html=True)

        # Check if the user has returned from Google authentication
        code = st.query_params.get("code")
        if code:
            try:
                # Exchange the code for a token and get user info
                user_info = exchange_code_for_token(code)
                #st.session_state["user_id"] = user_info["uid"]
                #st.session_state["authenticated"] = True
                st.query_params.clear()
                st.query_params["authenticated"] = "true"
                st.rerun()
            except Exception as e:
                st.error(f"Failed to authenticate with Google: {str(e)}")
    else:
        st.error("Google Client ID not found. Please set the GOOGLE_CLIENT_ID environment variable.")
        
        
# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load HTML content based on the selected menu item
def load_html(file_name):
    html_file = os.path.join(base_dir, file_name)
    with open(html_file) as f:
        html_content = f.read()
    return html_content

# Function to handle logout
def handle_logout():
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Set the just_logged_out flag
    st.session_state["just_logged_out"] = True
    
    # Clear all query parameters
    st.query_params.clear()
    
    # Determine the redirect URL based on the environment
    if os.getenv("ENVIRONMENT") == 'development':
        redirect_url = "http://localhost:8501"
    else:
        redirect_url = "https://coffee-bean-app-high-v1.streamlit.app/"
    
    # Provide a clickable link
    st.markdown(f"""
    <p>You have been logged out successfully. <br> Click
    <a href="{redirect_url}" target="_blank" class="button">here</a> to be redirected to the home page & close the old tab.</p>
    """, unsafe_allow_html=True)
    
    # Stop further processing to ensure the user is redirected
    st.stop()
    

def show_menu(default_index=0):
    with st.sidebar:
        return option_menu(
            "Menu",
            ["Home", "Predict", "Game", "Edu Blog", "Flavor Wheel", "My Account", "Logout"],
            icons=["house", "camera", "controller", "book", "circle", "person", "door-open"],
            menu_icon="cast",
            default_index=default_index,
            key="main_menu"  # Add this line
        )



#FUNCTION FOR EDU BLOG 
def show_blog_article():
    import edu_blog
    edu_blog.show_edu_blog_page()
    
def main():
    css_path = os.path.join(os.path.dirname(__file__), 'style.css')
    load_css(css_path)  # Load CSS

    # Check for authentication status
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = st.query_params.get("authenticated") == "true"
        
    # Check if we have just logged out
    just_logged_out = st.session_state.get("just_logged_out", False)
    if just_logged_out:
        st.session_state["just_logged_out"] = False
        st.query_params()
        st.rerun()
        return  # Exit the function early to avoid processing any leftover auth code
        
    # Check if we have a code from Google OAuth
    code = st.query_params.get("code")
    if code and not st.session_state["authenticated"]:
        user_info = exchange_code_for_token(code)
        if user_info:
            st.session_state["authenticated"] = True
            st.query_params["authenticated"] = "true"
            st.rerun()

    if st.session_state["authenticated"]:
        # User is authenticated, show the authenticated user menu
        st.sidebar.write("Authenticated User Menu")
        
        # Check if a specific page is requested in the URL
        requested_page = st.query_params.get("page", None)
        
        # Set the default index for the menu
        default_index = 0
        if requested_page == "edu_blog":
            default_index = 3  # Index of "Edu Blog" in the menu list
        
        # Show the menu with the correct default index
        selected = show_menu(default_index)
        
        if requested_page == "edu_blog" or selected == "Edu Blog":
            if 'viewing_blog' in st.session_state:
                st.session_state.viewing_blog = None
            st.markdown(load_html("edu_blog.html"), unsafe_allow_html=True)
            import edu_blog
            edu_blog.show_edu_blog_page()
        elif selected == "Home":
            st.markdown('<div class="page-home">', unsafe_allow_html=True)
            st.markdown(load_html("dashboard.html"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        elif selected == "Predict":
            st.markdown(load_html("predict.html"), unsafe_allow_html=True)
            import predict
            predict.show_predict_page()
        elif selected == "Game":
            st.markdown(load_html("game.html"), unsafe_allow_html=True)
            import game
            game.show_game_page()
        elif selected == "Flavor Wheel":
            st.markdown(load_html("flavor_wheel.html"), unsafe_allow_html=True)
            import flavor_wheel
            flavor_wheel.show_coffee_wheel_page()
        elif selected == "My Account":
            st.markdown(load_html("my_account.html"), unsafe_allow_html=True)
            import my_account
            my_account.show_my_account_page()
        elif selected == "Logout":
            handle_logout()
        else:
            # Default to Home if no valid selection
            st.markdown(load_html("dashboard.html"), unsafe_allow_html=True)
    else:
        # User is not authenticated
        # Check if we have a code from Google OAuth
        code = st.query_params.get("code")
        if code:
            try:
                exchange_code_for_token(code)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to authenticate with Google: {str(e)}")
        
        # Check if a specific blog is requested
        blog_index = st.query_params.get("blog")
        
        if blog_index is not None:
            # If a specific blog is requested, show only the blog article without sidebar
            show_blog_article()
        else:
            option = st.sidebar.selectbox("Select Option", ["Home", "Sign In", "Register"], key="main_selectbox")
            if option == "Sign In":
                show_sign_in_page()
            elif option == "Register":
                show_register_page()
            elif option == "Home":
                show_landing_page()
    
    # Don't clear the 'page' query parameter here
    # This allows the 'edu_blog' page to persist when "Read More" is clicked


if __name__ == "__main__":
    main()