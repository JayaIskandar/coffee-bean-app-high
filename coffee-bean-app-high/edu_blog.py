import streamlit as st
from urllib.parse import urlencode

from streamlit_js_eval import streamlit_js_eval

from streamlit_star_rating import st_star_rating

from firebase_config import db, auth  # Import your Firebase configuration
from firebase_admin import credentials, auth, firestore


def show_edu_blog_page():
    
    # Initialize session state for blog viewing
    if 'viewing_blog' not in st.session_state:
        st.session_state.viewing_blog = None

    # Get URL parameters to check if a specific blog is selected
    selected_blog_index = st.query_params.get("blog", None)

    # Update session state if a blog is selected via URL
    if selected_blog_index is not None:
        st.session_state.viewing_blog = int(selected_blog_index)

    # Define blog posts
    blogs = [
        {
            "title": "Understanding Arabica Coffee Beans",
            "excerpt": "Arabica coffee beans are known for their smooth, complex flavor profile...",
            "content": "Arabica coffee beans are the most popular type of coffee beans in the world. They are grown in higher altitudes and are known for their smooth, complex flavor profile, with hints of sweetness and acidity. The beans are oval in shape with a curved crease on one side. Arabica coffee is often considered to have a more delicate and nuanced flavor compared to Robusta coffee."
        },
        {
            "title": "Exploring the Richness of Robusta Coffee Beans",
            "excerpt": "Robusta coffee beans are known for their strong, bold flavor...",
            "content": "Robusta coffee beans are the second most popular type of coffee beans. They are typically grown at lower altitudes and are known for their strong, bold flavor with a more bitter taste. The beans are rounder and smaller compared to Arabica beans and have a straight crease. Robusta coffee is often used in espresso blends because of its rich crema and higher caffeine content."
        },
        {
            "title": "The Unique Flavor of Liberica Coffee Beans",
            "excerpt": "Liberica coffee beans have a distinctive flavor profile that sets them apart...",
            "content": "Liberica coffee beans are less common but have a unique flavor profile that is highly distinctive. They are larger and more irregular in shape compared to Arabica and Robusta beans. Liberica coffee has a bold, smoky flavor with fruity and floral notes. It is grown mainly in the Philippines and Malaysia, and its unique taste makes it a specialty coffee that is enjoyed by coffee enthusiasts around the world."
        }
    ]

    if selected_blog_index is None:
        st.title("Edu Blog Page")
        st.write("Welcome to the Edu Blog! Here you'll find interesting articles about coffee beans.")
        
        # Display blog posts as cards
        for i, blog in enumerate(blogs):
            st.markdown(
                f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                    <h3>{blog['title']}</h3>
                    <p>{blog['excerpt']}</p>
                    <a href="?{urlencode({'blog': i, 'authenticated': 'true', 'page': 'edu_blog'})}", target="_self">
                        <button>Read More</button>
                    </a>
                </div>
                """, unsafe_allow_html=True
            )
    else:
        selected_blog_index = int(selected_blog_index)
        if selected_blog_index < len(blogs):
            blog = blogs[selected_blog_index]
            st.title(blog["title"])
            st.write(blog["content"])
            
            
            # Custom CSS for rounded corners

            
            
            # Add rating form
            st.write("---")
            st.subheader("Rate this article")
            with st.form(key="rating_form"):
                stars = st_star_rating(label = "How's this article?", maxValue = 5, defaultValue = 3, key = "rating", dark_theme = False)
                comment = st.text_area("Your Comment")
                submit_button = st.form_submit_button(label="Submit Rating")

            if submit_button:
                # Here you would typically save the rating and comment to a database
                # Check if user is logged in (assume user_uid is stored in session state)
                #if 'user' in st.session_state and 'uid' in st.session_state['user']:
                    #user_uid = st.session_state['user']['uid']
                    # Save feedback to Firestore
                    feedback_ref = db.collection("feedbacks").document()
                    feedback_data = {
                        #"user_uid": user_uid,
                        "blog_index": selected_blog_index,
                        "rating": stars,
                        "comment": comment,
                        "createdAt": firestore.SERVER_TIMESTAMP
                    }
                    feedback_ref.set(feedback_data)
                    st.success(f"Thank you for your rating of {stars} stars and your comment!")
            else:
                    st.error("Please log in to submit feedback.")
            
            
            
            if st.button("Back to Home"):
                st.session_state.viewing_blog = None
                st.query_params.clear()
                st.switch_page("main.py")
                st.rerun()
                st.rerun()
                streamlit_js_eval(js_expressions="parent.window.location.reload()")

# Call the function in main.py
if __name__ == "__main__":
    show_edu_blog_page()