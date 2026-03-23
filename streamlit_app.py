import streamlit as st
import random
import os
import cv2
from PIL import Image

from facecode_core import FaceCodeCore
from face_emotion_module import EmotionDetector

API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="FaceCode", layout="wide")

st.title("🧠 FaceCode — Adaptive AI Coding Tutor")

# Initialize session state
if "core" not in st.session_state:
    st.session_state.core = FaceCodeCore(API_KEY)

if "emotion_detector" not in st.session_state:
    st.session_state.emotion_detector = EmotionDetector()

if "questions" not in st.session_state:
    st.session_state.questions = {
        "Easy": [
            "Write a function to check if a number is even.",
            "Return sum of a list."
        ],
        "Medium": [
            "Reverse a string.",
            "Find second largest element in list."
        ],
        "Hard": [
            "Implement stack using two queues.",
            "Longest substring without repeating characters."
        ]
    }

if "current_problem" not in st.session_state:
    st.session_state.current_problem = random.choice(
        st.session_state.questions["Medium"]
    )

# Layout
col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("Problem")

    st.write(st.session_state.current_problem)

    code = st.text_area(
        "Write your Python code:",
        height=300
    )

    if st.button("Evaluate Code"):

        if not code.strip():
            st.warning("Please write some code first.")
        else:

            emotion, emotion_conf = (
                st.session_state.emotion_detector.get_emotion_state()
            )

            # Dummy typing confidence (Streamlit cannot track keystrokes easily)
            typing_conf = 60

            result = st.session_state.core.evaluate_student(
                st.session_state.current_problem,
                code,
                typing_conf,
                emotion,
                emotion_conf,
                10
            )

            st.success("Evaluation Complete")

            st.markdown("### Explanation")
            st.write(result["error_explanation"])

            st.markdown("### Hint")
            st.write(result["hint"])

            st.markdown("### Reasoning")
            st.write(result["reason"])

            st.markdown("### System Stats")

            st.write(
                f"Difficulty: **{result['difficulty']}**  |  "
                f"Confidence: **{result['final_confidence']:.1f}%**  |  "
                f"Emotion: **{emotion}**"
            )

            # Update problem
            st.session_state.current_problem = random.choice(
                st.session_state.questions[result["difficulty"]]
            )

with col2:

    st.subheader("Camera")

    frame = st.session_state.emotion_detector.get_latest_frame()

    if frame is not None:

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        st.image(frame, channels="RGB")

    st.info(
        "Emotion detection is running in the background."
    )