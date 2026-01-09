from google import genai
import json
import re

API_KEY = "AIzaSyDywrnAzLhBivZW4DVqepCDph8-ufsiln8"

def validate_ideal_answers(compiled_exam: str):
    client = genai.Client(api_key=API_KEY)

    prompt = f"""
You are an expert subject-matter validator.

TASK:
- Validate whether the IDEAL ANSWERS correctly answer their respective questions.
- Do NOT consider student answers.
- Judge correctness, relevance, and conceptual accuracy.
- Mark pass only if answer is at least 80% correct.

RETURN STRICT JSON ONLY:

{{
  "overall_status": "pass | fail",
  "summary": "Short summary",
  "question_validation": [
    {{
      "question_no": 1,
      "status": "pass | fail",
      "confidence": 85,
      "comment": "Reason"
    }}
  ]
}}

CONTENT:
{compiled_exam}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return {"error": "Invalid response", "raw": text}

    return json.loads(match.group())
