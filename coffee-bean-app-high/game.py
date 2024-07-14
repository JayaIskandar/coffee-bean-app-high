import streamlit as st
import json
import os
import time
from datetime import datetime
from firebase_config import initialize_firebase, db, firestore

# Define base directory where the JSON file is located
base_dir = os.path.abspath(os.path.dirname(__file__))
css_path = os.path.join(base_dir, 'style.css')

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
    st.session_state.nickname = None
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
    st.title("Leaderboard")
    leaderboard = get_leaderboard()
    leaderboard_html = "<div class='leaderboard-card'>"
    for idx, entry in enumerate(leaderboard):
        data = entry.to_dict()
        total_seconds_rounded = round(data['total_seconds'], 1)
        leaderboard_html += f"<div class='leaderboard-entry'>{idx + 1}. {data['nickname']} - {data['score']} points - {total_seconds_rounded} seconds</div>"
    leaderboard_html += "</div>"
    st.markdown(leaderboard_html, unsafe_allow_html=True)


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
                st.experimental_rerun()
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

                st.write(f"**Current Level: {level.capitalize()}**")
                st.write(f"**Question: {question_index + 1}/{len(current_questions)}**")

                # Display hearts for lives
                st.markdown(
                    f"<p class='hearts'>{'❤️' * lives} {'🤍' * (5 - lives)}</p>", 
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="question-container">
                        <p>{q["question"]}</p>
                    </div>
                    """, unsafe_allow_html=True
                )

                answer = st.radio("Choose your answer:", q["options"], key=f"q{question_index}")

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
                    st.experimental_rerun()

            else:
                ################# IF LOSE THE GAME #####################
                total_time = (datetime.now() - st.session_state.start_time).total_seconds()
                save_score_to_firestore(st.session_state.nickname, score, total_time)
                st.write(f"Game Over! Your final score is: {score}")
                st.write(f"Time taken: {total_time:.1f} seconds")
                st.snow()
                show_leaderboard()
                st.session_state.game_started = False
                reset_game_state()

        else:
            ################# IF WIN THE GAME #####################
            total_time = (datetime.now() - st.session_state.start_time).total_seconds()
            save_score_to_firestore(st.session_state.nickname, score, total_time)
            st.write(f"Congratulations! You've completed all levels. Your final score is: {score}")
            st.write(f"Time taken: {total_time:.1f} seconds")
            st.balloons()
            show_leaderboard()
            st.session_state.game_started = False
            reset_game_state()

        # Reset the game state
        if st.button("Play Again"):
            reset_game_state()
            st.experimental_rerun()

# Call the function in your main script
if __name__ == "__main__":
    show_game_page()
