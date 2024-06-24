import streamlit as st
import os
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
from firebase_config import initialize_firebase, create_user_with_email_password

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase SDK
initialize_firebase()

# Determine the environment based on the URL
if "localhost" in os.getenv("BASE_URL_DEV", ""):
    base_url = os.getenv("BASE_URL_DEV")
else:
    base_url = os.getenv("BASE_URL_PROD")

# Define base directory where HTML files are located
base_dir = os.path.abspath(os.path.dirname(__file__))

def show_sign_in_page():
    st.title("Sign In")
    provider = st.selectbox("Select Provider", ["Google", "Email/Password"])
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")  # Retrieve Google Client ID from environment variable
    if provider == "Google" and google_client_id:
        sign_in_url = f"https://accounts.google.com/o/oauth2/auth?client_id={google_client_id}&redirect_uri={base_url}&response_type=code&scope=email"
        st.markdown(f'[Sign in with Google]({sign_in_url})', unsafe_allow_html=True)
    elif provider == "Email/Password":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign In"):
            # Implement Firebase sign-in logic here
            # Example logic to handle sign-in
            # if successful:
            st.session_state["authenticated"] = True
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
                st.success("A verification email has been sent to your email address.")
            else:
                st.error("Failed to create user. Please try again.")

################################################################
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

################################################################

# Function to handle logout
def handle_logout():
    st.session_state["authenticated"] = False
    st.rerun()
    
def main():
    css_path = os.path.join(os.path.dirname(__file__), 'style.css')
    load_css(css_path)  # Load CSS

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        option = st.sidebar.selectbox("Select Option", ["Sign In", "Register"])
        if option == "Sign In":
            show_sign_in_page()
        elif option == "Register":
            show_register_page()
    else:
        st.sidebar.write("Authenticated User Menu")
        # Create the navigation menu
        with st.sidebar:
            selected = option_menu(
                "Menu",
                ["Home", "Predict", "Game", "Edu Blog", "Flavor Wheel", "My Account", "Logout"],
                icons=["house", "camera", "controller", "book", "circle", "person", "door-open"],
                menu_icon="cast",
                default_index=0,
            )
        
        # 2. horizontal menu
        #selected2 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
        #    icons=['house', 'cloud-upload', "list-task", 'gear'], 
        #    menu_icon="cast", default_index=0, orientation="horizontal")
        
        if selected == "Home":
            st.markdown(load_html("landing.html"), unsafe_allow_html=True)
        elif selected == "Predict":
            st.markdown(load_html("predict.html"), unsafe_allow_html=True)
            import predict
            predict.show_predict_page()
        elif selected == "Game":
            st.markdown(load_html("game.html"), unsafe_allow_html=True)
            import game
            game.show_game_page()
        elif selected == "Edu Blog":
            st.markdown(load_html("edu_blog.html"), unsafe_allow_html=True)
            import edu_blog
            edu_blog.show_edu_blog_page()
        elif selected == "Flavor Wheel":
            st.markdown(load_html("flavor_wheel.html"), unsafe_allow_html=True)
            import flavor_wheel
            flavor_wheel.show_flavor_wheel_page()
        elif selected == "My Account":
            st.markdown(load_html("my_account.html"), unsafe_allow_html=True)
            import my_account
            my_account.show_my_account_page()
        elif selected == "Logout":
            handle_logout()

if __name__ == "__main__":
    main()


