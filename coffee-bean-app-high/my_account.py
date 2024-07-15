import streamlit as st
from firebase_config import initialize_firebase, db

def show_my_account_page():
    st.title("Account Page")
    
    initialize_firebase()  # Ensure Firebase is initialized
    
    if 'user' not in st.session_state:
        st.error("User not authenticated")
        return
    
    user_id = st.session_state['user']
    
    # Retrieve user details from Firestore
    user_ref = db.collection("users").document(user_id)
    user_details = user_ref.get()
    
    if user_details.exists:
        user_data = user_details.to_dict()
        st.write("Account Details")
        st.write(f"Email: {user_data.get('email', 'N/A')}")
        st.write(f"User ID: {user_data.get('uid', 'N/A')}")
        st.write(f"Account Created At: {user_data.get('createdAt', 'N/A')}")
    else:
        st.error("User details not found.")

# Call this function to display the account page
show_my_account_page()
