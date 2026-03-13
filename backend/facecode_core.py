# facecode_core.py

from llm_tutor_module import LLMTutor


class FaceCodeCore:

    def __init__(self, api_key):
        self.tutor = LLMTutor(api_key)
        self.current_difficulty = "Medium"
        self.hints_used = 0
        self.session_history = []

    # -------------------------
    # Confidence Fusion Engine
    # -------------------------

    def fuse_confidence(self, typing_conf, emotion_conf, emotion_state):

        modifier = 0

        if emotion_state == "confident":
            modifier = 8
        elif emotion_state == "struggling":
            modifier = -12

        fused = (
            0.6 * typing_conf +
            0.4 * emotion_conf +
            modifier
        )

        return max(0, min(fused, 100))

    # -------------------------
    # Deterministic Difficulty Engine
    # -------------------------

    def update_difficulty(self, final_conf):

        # Store recent confidence
        self.session_history.append(final_conf)

        # Only adjust after 3 evaluations
        if len(self.session_history) < 3:
            return False

        recent_avg = sum(self.session_history[-3:]) / 3

        if recent_avg >= 70:
            if self.current_difficulty == "Easy":
                self.current_difficulty = "Medium"
            elif self.current_difficulty == "Medium":
                self.current_difficulty = "Hard"
            return True

        elif recent_avg <= 45:
            if self.current_difficulty == "Hard":
                self.current_difficulty = "Medium"
            elif self.current_difficulty == "Medium":
                self.current_difficulty = "Easy"
            return True

        return False
    # -------------------------
    # Main Evaluation
    # -------------------------

    def evaluate_student(
        self,
        problem,
        student_code,
        typing_conf,
        emotion_state,
        emotion_conf,
        time_taken
    ):

        final_conf = self.fuse_confidence(
            typing_conf,
            emotion_conf,
            emotion_state
        )

        llm_feedback = self.tutor.evaluate_code(
            problem,
            student_code,
            final_conf,
            emotion_state,
            self.current_difficulty,
            self.hints_used,
            time_taken
        )

        difficulty_changed = self.update_difficulty(final_conf)

        self.hints_used += 1

        self.session_history.append({
            "confidence": final_conf,
            "difficulty": self.current_difficulty
        })

        return {
            "final_confidence": final_conf,
            "difficulty": self.current_difficulty,
            "difficulty_changed": difficulty_changed,
            "error_explanation": llm_feedback.get("error_explanation"),
            "hint": llm_feedback.get("hint"),
            "reason": llm_feedback.get("reason")
        }