import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ----------------------------
# Professor Email (Hard-coded)
# ----------------------------
PROF_EMAIL = "profbgubbsr@gmail.com"
PROF_PASSWORD = "bdif yvjh edbi krcs"


def send_result_email(student_email: str, student_id: str, result: dict):
    msg = MIMEMultipart()
    msg["From"] = PROF_EMAIL
    msg["To"] = student_email
    msg["Subject"] = f"Exam Evaluation Result | Student ID: {student_id}"

    body = f"""
Hello Student,

Your answer sheet has been evaluated successfully.

----------------------------
RESULT SUMMARY
----------------------------

Total Score:
{result.get('total_score', 'N/A')}

Overall Feedback:
{result.get('overall_feedback', 'N/A')}

----------------------------
QUESTION-WISE MARKS
----------------------------
"""

    for q in result.get("question_wise_marks", []):
        body += (
            f"\nQuestion {q['question_no']}: "
            f"{q['marks_awarded']} / {q['max_marks']}\n"
            f"Reason: {q['reason']}\n"
        )

    if "ai_content_percentage" in result:
        body += f"\nAI Content Detected: {result['ai_content_percentage']}%\n"

    body += "\nRegards,\nProfessor"

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(PROF_EMAIL, PROF_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email sending failed:", e)
