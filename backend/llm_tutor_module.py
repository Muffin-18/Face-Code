# llm_tutor_module.py

import json
from groq import Groq


class LLMTutor:
    """
    FaceCode LLM Tutor Module (Groq)
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GROQ_API_KEY not found.")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def build_prompt(
        self,
        problem,
        student_code,
        confidence,
        emotion,
        difficulty,
        hints_used,
        time_taken
    ):

        return f"""
You are an AI coding tutor inside FaceCode.

Student Stats:
Confidence: {confidence:.2f}%
Emotion: {emotion}
Difficulty: {difficulty}
Hints Used: {hints_used}
Time (sec): {time_taken:.1f}

Problem:
{problem}

Student Code:
{student_code}

Rules:
- Never reveal full solution.
- Provide explanation + controlled hint.
- Keep output strict JSON only.

Return:

{{
  "error_explanation": "...",
  "hint": "...",
  "reason": "short reasoning"
}}
"""

    def evaluate_code(
        self,
        problem,
        student_code,
        confidence,
        emotion,
        difficulty,
        hints_used,
        time_taken
    ):

        prompt = self.build_prompt(
            problem,
            student_code,
            confidence,
            emotion,
            difficulty,
            hints_used,
            time_taken
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are a precise JSON generator."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        try:
            return json.loads(content)
        except:
            return {
                "error_explanation": "Unable to parse structured feedback.",
                "hint": content,
                "reason": "Fallback mode."
            }
