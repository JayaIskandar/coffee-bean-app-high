import streamlit as st
import os

# Set page config at the very beginning
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Remove default Streamlit styling
st.markdown("""
    <style>
        .stApp {
            margin: 0;
            padding: 0;
        }
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

# Load HTML content
def load_html(file_name):
    html_file = os.path.join(os.path.dirname(__file__), file_name)
    with open(html_file, 'r', encoding='utf-8') as f:
        return f.read()

# Load and display HTML content
html_content = load_html('landing.html')
st.html(html_content)

# Button to switch to the main application (placed at the bottom of the HTML content)
st.markdown("""
    <div style="position: fixed; bottom: 20px; right: 20px;">
        <button onclick="document.getElementById('go-to-main').click()" style="padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
            Go to Main Application
        </button>
    </div>
""", unsafe_allow_html=True)

if st.button("Go to Main Application", key="go-to-main"):
    try:
        st.switch_page("./main.py")
    except st.errors.StreamlitAPIException:
        st.error("Could not switch to main.py directly. Trying alternative method.")
        import main
        main.main()  # Assuming main.py has a main() function that runs the app