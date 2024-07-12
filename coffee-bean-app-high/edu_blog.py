import streamlit as st
from urllib.parse import urlencode

def show_edu_blog_page():
    
    # Initialize session state for blog viewing
    if 'viewing_blog' not in st.session_state:
        st.session_state.viewing_blog = None

    # Check for a reset parameter
    if st.query_params.get("reset") == "true":
        st.session_state.viewing_blog = None
        st.query_params.clear()
        st.query_params(authenticated='true', page='edu_blog')
        st.rerun()
        
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

    if st.session_state.viewing_blog is None:
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
        if st.session_state.viewing_blog < len(blogs):
            blog = blogs[st.session_state.viewing_blog]

            st.title(blog["title"])
            st.write(blog["content"])
            if st.button("Back to Home"):
                st.session_state.viewing_blog = None
                st.query_params.clear()
                st.switch_page("main.py")

# Call the function in main.py
if __name__ == "__main__":
    show_edu_blog_page()