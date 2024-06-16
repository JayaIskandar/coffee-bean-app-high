import streamlit as st
from streamlit_option_menu import option_menu
import os

# Set the working directory to the script's directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load HTML content based on the selected menu item
def load_html(menu_item):
    html_file = os.path.join(base_dir, f'{menu_item.lower()}.html')
    with open(html_file) as f:
        html_content = f.read()
    return html_content

# Main function
def main():
    css_path = os.path.join(base_dir, 'style.css')
    load_css(css_path)  # Load CSS

    # Create the navigation menu
    with st.sidebar:
        selected = option_menu(
            "Menu",
            ["Predict", "Game", "Edu Blog", "Flavor Wheel", "My Account"],
            icons=["camera", "controller", "book", "circle", "person"],
            menu_icon="cast",
            default_index=0,
        )

    # Display content based on selected menu item
    if selected == "Predict":
        st.markdown(load_html("predict"), unsafe_allow_html=True)

        # Import and show predict page
        import predict
        predict.show_predict_page()

    elif selected == "Game":
        st.markdown(load_html("game"), unsafe_allow_html=True)

        # Import and show game page
        import game
        game.show_game_page()

    elif selected == "Edu Blog":
        st.markdown(load_html("edu_blog"), unsafe_allow_html=True)

        # Import and show edu blog page
        import edu_blog
        edu_blog.show_edu_blog_page()

    elif selected == "Flavor Wheel":
        st.markdown(load_html("flavor_wheel"), unsafe_allow_html=True)

        # Import and show flavor wheel page
        import flavor_wheel
        flavor_wheel.show_flavor_wheel_page()

    elif selected == "My Account":
        st.markdown(load_html("my_account"), unsafe_allow_html=True)

        # Import and show my account page
        import my_account
        my_account.show_my_account_page()

if __name__ == "__main__":
    main()
