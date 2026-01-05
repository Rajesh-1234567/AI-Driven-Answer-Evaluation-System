# app/gemini_eval.py

from google import genai
import json
import re

# 🔐 HARD-CODED API KEY (as requested)
API_KEY = "YOUR KEY"


def evaluate_answers(compiled_exam: str, evaluation_style: str, student_text: str):
    client = genai.Client(api_key=API_KEY)

    prompt = f"""
You are an unbiased exam evaluator.

INPUTS:
1. Exam questions with ideal answers and marks
2. Teacher evaluation instructions
3. Student answer sheet text (OCR)

TASK:
- Match answers to questions automatically
- Evaluate strictly using ideal answers
- Award marks per question (do NOT exceed max marks)
- Give short justification per question
- Calculate total score
- Provide overall feedback

RULES:
- Missing answer = 0 marks
- Partial answer = partial marks
- Ignore grammar & handwriting
- Be consistent

OUTPUT:
Return ONLY valid JSON in this format:

{{
  "question_wise_marks": [
    {{
      "question_no": 1,
      "marks_awarded": 3,
      "max_marks": 5,
      "reason": "Short explanation"
    }}
  ],
  "total_score": "18/25",
  "overall_feedback": "Short feedback"
}}

--------------------
EXAM:
{compiled_exam}

--------------------
TEACHER INSTRUCTIONS:
{evaluation_style}

--------------------
STUDENT ANSWERS:
{student_text}
"""

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

    return json.loads(match.group())
