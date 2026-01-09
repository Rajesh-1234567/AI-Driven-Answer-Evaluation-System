# app/gemini_eval.py

from google import genai
import json
import re

API_KEY = "AIzaSyDywrnAzLhBivZW4DVqepCDph8-ufsiln8"


def evaluate_answers(compiled_exam: str, evaluation_style: str, student_text: str):
    client = genai.Client(api_key=API_KEY)

    prompt = (
        "You are an unbiased exam evaluator.\n\n"
        "TASKS:\n"
        "1. Evaluate answers question-wise.\n"
        "2. Award marks strictly.\n"
        "3. Give short justification per question.\n"
        "4. Calculate total score.\n"
        "5. Detect AI-generated content percentage.\n\n"
        "RETURN STRICT JSON ONLY:\n"
        "{\n"
        '  "question_wise_marks": [\n'
        "    {\n"
        '      "question_no": 1,\n'
        '      "marks_awarded": 3,\n'
        '      "max_marks": 5,\n'
        '      "reason": "Explanation"\n'
        "    }\n"
        "  ],\n"
        '  "total_score": "18/25",\n'
        '  "overall_feedback": "Feedback",\n'
        '  "ai_content_percentage": 35,\n'
        '  "ai_analysis_reason": "Reason for AI usage score"\n'
        "}\n\n"
        "EXAM:\n"
        + compiled_exam
        + "\n\nTEACHER INSTRUCTIONS:\n"
        + evaluation_style
        + "\n\nSTUDENT ANSWERS:\n"
        + student_text
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
    except Exception as e:
        return {
            "error": "Gemini API error",
            "details": str(e)
        }

    text = response.text.strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {
            "error": "Invalid Gemini response",
            "raw_output": text
        }

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {
            "error": "JSON parsing failed",
            "raw_output": text
        }
