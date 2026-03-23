# facecode_gui.py

import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk
import cv2
import os
import random

from facecode_core import FaceCodeCore
from typing_speed_tracker import TypingSpeedTracker
from face_emotion_module import EmotionDetector


API_KEY = os.getenv("GROQ_API_KEY")


class FaceCodeGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("FaceCode – Adaptive AI Coding Platform")
        self.root.geometry("1300x800")

        self.core = FaceCodeCore(API_KEY)
        self.emotion_detector = EmotionDetector()

        self.questions = {
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

        self.current_problem = random.choice(self.questions["Medium"])

        left = tk.Frame(root)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(root)
        right.pack(side="right", fill="y")

        self.problem_label = tk.Label(
            left,
            text=f"Problem: {self.current_problem}",
            font=("Arial", 14),
            wraplength=900,
            justify="left"
        )
        self.problem_label.pack(anchor="w", padx=10, pady=5)

        self.stats_label = tk.Label(
            left,
            text="Difficulty: Medium | Confidence: -- | Emotion: --",
            fg="blue"
        )
        self.stats_label.pack(anchor="w", padx=10)

        self.code_editor = scrolledtext.ScrolledText(left, font=("Consolas", 12))
        self.code_editor.pack(fill="both", expand=True, padx=10, pady=10)

        self.typing_tracker = TypingSpeedTracker(self.code_editor)

        tk.Button(
            left,
            text="Evaluate Code",
            command=self.evaluate_code,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=5)

        self.feedback = scrolledtext.ScrolledText(left, height=10)
        self.feedback.pack(fill="both", expand=True, padx=10, pady=10)

        self.camera_label = tk.Label(right)
        self.camera_label.pack(padx=10, pady=10)

        self.update_camera()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def update_camera(self):

        frame = self.emotion_detector.get_latest_frame()

        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame).resize((400, 300))
            imgtk = ImageTk.PhotoImage(img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        self.root.after(30, self.update_camera)

    def evaluate_code(self):

        code = self.code_editor.get("1.0", tk.END).strip()

        if not code:
            messagebox.showwarning("Warning", "Write some code first.")
            return

        typing_conf, idle, acc = self.typing_tracker.get_typing_metrics()
        emotion, emotion_conf = self.emotion_detector.get_emotion_state()

        result = self.core.evaluate_student(
            self.current_problem,
            code,
            typing_conf,
            emotion,
            emotion_conf,
            idle
        )

        self.stats_label.config(
            text=f"Difficulty: {result['difficulty']} | "
                 f"Confidence: {result['final_confidence']:.1f}% | "
                 f"Emotion: {emotion}"
        )

        self.feedback.delete("1.0", tk.END)
        self.feedback.insert(tk.END, result["error_explanation"] + "\n\n")
        self.feedback.insert(tk.END, result["hint"] + "\n\n")
        self.feedback.insert(tk.END, result["reason"])

        self.current_problem = random.choice(
            self.questions[result["difficulty"]]
        )

        self.problem_label.config(
            text=f"Problem: {self.current_problem}"
        )

        self.code_editor.delete("1.0", tk.END)

    def close(self):
        self.emotion_detector.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceCodeGUI(root)
    root.mainloop()