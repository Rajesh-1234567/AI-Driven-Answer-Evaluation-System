from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from ocr import extract_text_from_pdf
from gemini_eval import evaluate_answers

st.set_page_config(page_title="AI Answer Evaluator")
st.title("📝 AI Answer Evaluation System")

st.info("Fresh app • No cache • No memory • Refresh = reset")

# -------------------------------------------------
# Session state init (ONLY what we need)
# -------------------------------------------------
if "compiled_exam" not in st.session_state:
    st.session_state.compiled_exam = None

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None

# -------------------------------------------------
# 1️⃣ Exam Creation
# -------------------------------------------------
st.header("1️⃣ Create Exam")

num_questions = st.number_input(
    "Number of Questions",
    min_value=1,
    max_value=20,
    step=1,
    value=1
)

questions = []

for i in range(num_questions):
    st.subheader(f"Question {i + 1}")

    q = st.text_area("Question", key=f"q_{i}")
    a = st.text_area("Ideal Answer", key=f"a_{i}")
    m = st.number_input(
        "Max Marks",
        min_value=1,
        max_value=20,
        key=f"m_{i}"
    )

    questions.append({
        "question_no": i + 1,
        "question": q.strip(),
        "ideal_answer": a.strip(),
        "max_marks": m
    })

evaluation_style = st.text_area(
    "Teacher Evaluation Instructions",
    placeholder="Strict / Lenient / Step-wise / Concept-based etc.",
    height=120
)

# -------------------------------------------------
# 2️⃣ Compile Exam
# -------------------------------------------------
if st.button("📘 Compile Exam"):
    for q in questions:
        if not q["question"] or not q["ideal_answer"]:
            st.error("All questions and ideal answers are required")
            st.stop()

    if not evaluation_style.strip():
        st.error("Evaluation instructions required")
        st.stop()

    compiled_exam = ""
    total_marks = 0

    for q in questions:
        total_marks += q["max_marks"]
        compiled_exam += (
            f"Q{q['question_no']} ({q['max_marks']} marks)\n"
            f"Question:\n{q['question']}\n\n"
            f"Ideal Answer:\n{q['ideal_answer']}\n"
            f"{'-'*40}\n\n"
        )

    compiled_exam += f"\nEvaluation Instructions:\n{evaluation_style}"

    # ✅ STORE IN SESSION (THIS IS THE FIX)
    st.session_state.compiled_exam = compiled_exam

    st.success("Exam compiled successfully")

# Preview (if already compiled)
if st.session_state.compiled_exam:
    st.subheader("📘 Compiled Exam (Preview)")
    st.text_area(
        "This will be sent to the evaluator",
        st.session_state.compiled_exam,
        height=350
    )

# -------------------------------------------------
# 3️⃣ OCR Section
# -------------------------------------------------
st.divider()
st.header("2️⃣ Upload Student Answer Sheet (OCR)")

pdf = st.file_uploader("Upload PDF", type=["pdf"])

if pdf:
    os.makedirs("data", exist_ok=True)
    pdf_path = "data/temp.pdf"

    with open(pdf_path, "wb") as f:
        f.write(pdf.read())

    if st.button("📄 Extract Text"):
        with st.spinner("Running offline OCR..."):
            st.session_state.extracted_text = extract_text_from_pdf(pdf_path)

        st.success("OCR completed")

if st.session_state.extracted_text:
    st.text_area(
        "📄 Extracted Student Answers",
        st.session_state.extracted_text,
        height=300
    )

# -------------------------------------------------
# 4️⃣ Gemini Evaluation
# -------------------------------------------------
st.divider()
st.header("3️⃣ Evaluate Using Gemini")

if st.button("🧠 Evaluate Answer Sheet"):
    if not st.session_state.compiled_exam:
        st.error("Compile exam first")
        st.stop()

    if not st.session_state.extracted_text:
        st.error("Run OCR first")
        st.stop()

    if not evaluation_style.strip():
        st.error("Evaluation instructions missing")
        st.stop()

    with st.spinner("Evaluating with Gemini..."):
        result = evaluate_answers(
            st.session_state.compiled_exam,
            evaluation_style,
            st.session_state.extracted_text
        )

    if "error" in result:
        st.error(result["error"])
        st.caption(result.get("details", ""))
    else:
        st.success("Evaluation completed")

        st.subheader("📊 Question-wise Marks")
        for q in result["question_wise_marks"]:
            st.markdown(
                f"""
**Q{q['question_no']}** → {q['marks_awarded']} / {q['max_marks']}  
_Reason_: {q['reason']}
"""
            )

        st.subheader("🎯 Total Score")
        st.markdown(f"### **{result['total_score']}**")

        st.subheader("📝 Overall Feedback")
        st.info(result["overall_feedback"])
