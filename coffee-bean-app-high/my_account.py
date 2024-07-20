import streamlit as st
from firebase_config import initialize_firebase, db, update_user_password, delete_user_account

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
    
    # READ ACCOUNT DETAILS
    if user_details.exists:
        user_data = user_details.to_dict()
        st.write("Account Details")
        st.write(f"Email: {user_data.get('email', 'N/A')}")
        st.write(f"User ID: {user_data.get('uid', 'N/A')}")
        st.write(f"Account Created At: {user_data.get('createdAt', 'N/A')}")
        
        # UPDATE ACCOUNT DETAILS (PASSWORD AS OF NOW)
        st.write("Update Password")
        with st.form(key="unique_password_update_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            submitted = st.form_submit_button("Update Password")
            
            if submitted:
                if not new_password or not confirm_password:
                    st.error("Both password fields are required.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    # Update user password using Firebase Authentication
                    success = update_user_password(user_id, new_password)
                    if success:
                        st.success("Password updated successfully.")
                    else:
                        st.error("Failed to update password.")
        
        # DELETE ACCOUNT 
        st.write("Delete Account")
        confirm_delete = st.checkbox("I confirm that I want to delete my account and understand that this action cannot be undone.")
        if st.button("Delete Account"):
            if confirm_delete:
                success = delete_user_account(user_id)
                if success:
                    st.success("Account deleted successfully.")
                    
                    # Using meta refresh tag for redirection
                    st.markdown('<meta http-equiv="refresh" content="0; url=https://coffee-bean-app-high-v1.streamlit.app/">', unsafe_allow_html=True)
                    # Clear the session state
                    st.session_state.clear()
                    # Redirect using Streamlit's session state method
                    st.rerun()
                else:
                    st.error("Failed to delete account.")
            else:
                st.error("Please confirm that you want to delete your account.")
    else:
        st.error("User details not found.")

# Call this function to display the account page
show_my_account_page()
