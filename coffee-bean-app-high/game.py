import streamlit as st
import json
import os
import time
from datetime import datetime
from firebase_config import initialize_firebase, db, firestore

import base64

# Define base directory where the JSON file is located
base_dir = os.path.abspath(os.path.dirname(__file__))
css_path = os.path.join(base_dir, 'style.css')

wa_icon_path = os.path.join(base_dir, 'wa-icon.png')


# Initialize Firebase
initialize_firebase()

# Function to load questions from a JSON file
def load_questions():
    file_path = os.path.join(base_dir, "questions.json")
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

questions = load_questions()

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def reset_game_state():
    st.session_state.lives = 5
    st.session_state.score = 0
    st.session_state.level = "easy"
    st.session_state.question_index = 0
    st.session_state.start_time = None
    st.session_state.game_started = False

# Function to show toast message
def show_toast(message):
    toast_html = f"""
    <div id="toast">
      {message}
      <div></div>
    </div>
    """
    st.markdown(toast_html, unsafe_allow_html=True)

# Function to save the score and time to Firestore
def save_score_to_firestore(nickname, score, total_seconds):
    doc_ref = db.collection("leaderboard").document()
    doc_ref.set({
        "nickname": nickname,
        "score": score,
        "total_seconds": round(total_seconds, 1),
        "timestamp": firestore.SERVER_TIMESTAMP
    })

# Function to get the leaderboard from Firestore
def get_leaderboard():
    leaderboard_ref = db.collection("leaderboard").order_by("score", direction=firestore.Query.DESCENDING).order_by("total_seconds").limit(10)
    leaderboard = leaderboard_ref.get()
    return leaderboard

# Function to display the leaderboard
def show_leaderboard():
    st.title("Live Leaderboard")
    leaderboard = get_leaderboard()
    leaderboard_html = "<div class='leaderboard-card'>"
    for idx, entry in enumerate(leaderboard):
        data = entry.to_dict()
        total_seconds_rounded = round(data['total_seconds'], 1)
        leaderboard_html += f"<div class='leaderboard-entry'>{idx + 1}. {data['nickname']} - {data['score']} points - {total_seconds_rounded} seconds</div>"
    leaderboard_html += "</div>"
    st.markdown(leaderboard_html, unsafe_allow_html=True)

# Define your game URL
game_url = "https://coffee-bean-app-high-v1.streamlit.app/"

# Function to create social sharing links
def generate_share_link(score, nickname):
    whatsapp_message = f"{nickname} scored {score} points in the BeanXpert Coffee Quiz Game! Try to beat my score! {game_url}"
    whatsapp_url = f"https://api.whatsapp.com/send?text={whatsapp_message}"

    return whatsapp_url

# Function to encode image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

####################### START THE GAME #################################
def show_game_page():
    st.title("Coffee Quiz Game")

    # Load custom CSS
    load_css(css_path)

    if 'game_started' not in st.session_state:
        reset_game_state()

    if not st.session_state.game_started:
        with st.form("nickname_form"):
            nickname = st.text_input("Enter your nickname:")
            submit_button = st.form_submit_button("Start Game")
            if submit_button and nickname:
                st.session_state.nickname = nickname
                st.session_state.start_time = datetime.now()
                st.session_state.game_started = True
                st.rerun()
        show_leaderboard()

    if st.session_state.game_started:
        lives = st.session_state.lives
        score = st.session_state.score
        level = st.session_state.level
        question_index = st.session_state.question_index

        if level:
            current_questions = questions[level]

            if question_index < len(current_questions) and lives > 0:
                q = current_questions[question_index]

                # Displaying current level and question with larger font size
                st.markdown(f"""
                    <p style='font-size: 1.2rem; font-weight: bold;'>Current Level: &nbsp;{level.upper()}</p>
                    <p style='font-size: 1.2rem; font-weight: bold;'>Question: &nbsp;{question_index + 1}/{len(current_questions)}</p>
                """, unsafe_allow_html=True)

                # Display hearts for lives
                st.markdown(
                    f"<p class='hearts'>{'❤️' * lives} {'🤍' * (5 - lives)}</p>", 
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="question-container">
                        <p class="question-text">{q["question"]}</p>
                    </div>
                    """, unsafe_allow_html=True
                )

                # Display bold text with inline CSS
                st.markdown("""
                    <p style='font-weight: bold; font-size: 1.2rem; margin-top:20px; margin-bottom: -10px;'>Choose your answer:</p>
                """, unsafe_allow_html=True)

                
                # Radio button widget
                answer = st.radio("", q["options"], key=f"q{question_index}")

                if st.button("Submit Answer", key=f"submit{question_index}"):
                    if answer == q["answer"]:
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect! The correct answer is: {q['answer']}")

                    st.write(f"**Explanation:** {q['explanation']}")

                    # Show success or error message for a short duration
                    time.sleep(3)
                    show_toast("Proceeding to next question")
                    time.sleep(1.5)

                    score += 1 if answer == q["answer"] else 0
                    lives -= 1 if answer != q["answer"] else 0

                    st.session_state.lives = lives
                    st.session_state.score = score
                    st.session_state.question_index += 1

                    if st.session_state.question_index >= len(current_questions):
                        if level == "easy":
                            st.session_state.level = "medium"
                        elif level == "medium":
                            st.session_state.level = "hard"
                        else:
                            st.session_state.level = None
                        st.session_state.question_index = 0
                    st.rerun()

            else:
                ################# IF LOSE THE GAME #####################
                total_time = (datetime.now() - st.session_state.start_time).total_seconds()
                save_score_to_firestore(st.session_state.nickname, score, total_time)
                # Display the final score and time taken with larger font
                st.markdown(f"""
                    <p style='font-size: 1.5rem; font-weight: bold;'>Game Over!</p>
                    <p style='font-size: 1.5rem; font-weight: bold;'>Your final score is: {score}</p>
                    <p style='font-size: 1.5rem; font-weight: bold;'>Time taken: {total_time:.1f} seconds</p>
                """, unsafe_allow_html=True)
                st.snow()
                show_leaderboard()
                
                st.session_state.game_started = False
                # Generate share links if nickname is not None
                if st.session_state.nickname:
                    whatsapp_link = generate_share_link(score, st.session_state.nickname)
                    wa_icon_base64 = get_base64_image(wa_icon_path)
                    st.markdown(
                        f"""
                        <div>
                            <h3>Share your achievement!</h3>
                            <a href="{whatsapp_link}" target="_blank" class="social-button">
                                <img src="data:image/png;base64,{wa_icon_base64}" alt="WhatsApp" width="20" height="20">
                                Share on WhatsApp
                        </div>
                        """, unsafe_allow_html=True
                    )
                else:
                    st.warning("Nickname not set, unable to share.")
                
                # Reset the game state without clearing nickname
                reset_game_state()

        else:
            ################# IF WIN THE GAME #####################
            total_time = (datetime.now() - st.session_state.start_time).total_seconds()
            save_score_to_firestore(st.session_state.nickname, score, total_time)
            # Display the final score and time taken with larger font
            st.markdown(f"""
                <p style='font-size: 1.5rem; font-weight: bold;'>Congratulations!</p>
                <p style='font-size: 1.5rem; font-weight: bold;'>Your final score is: {score}</p>
                <p style='font-size: 1.5rem; font-weight: bold;'>Time taken: {total_time:.1f} seconds</p>
            """, unsafe_allow_html=True)
            st.balloons()
            show_leaderboard()
            st.session_state.game_started = False
            # Generate share links if nickname is not None
            if st.session_state.nickname:
                whatsapp_link = generate_share_link(score, st.session_state.nickname)
                wa_icon_base64 = get_base64_image(wa_icon_path)
                st.markdown(
                    f"""
                    <div>
                        <h4>Share your achievement!</h4>
                        <a href="{whatsapp_link}" target="_blank" class="social-button">
                            <img src="data:image/png;base64,{wa_icon_base64}" alt="WhatsApp" width="20" height="20">
                            Share on WhatsApp
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                st.warning("Nickname not set, unable to share.")
                
            # Reset the game state without clearing nickname
            reset_game_state()

        # Reset the game state and clear the nickname
        if st.button("Play Again"):
            st.session_state.nickname = None
            reset_game_state()
            st.rerun()

# Call the function in your main script
if __name__ == "__main__":
    show_game_page()
