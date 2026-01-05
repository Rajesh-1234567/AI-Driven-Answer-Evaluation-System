import pytesseract
from pdf2image import convert_from_path


def extract_text_from_pdf(pdf_path: str) -> str:
    images = convert_from_path(pdf_path)
    text = ""

    for i, img in enumerate(images):
        page_text = pytesseract.image_to_string(img)
        text += f"\n--- Page {i+1} ---\n{page_text}"

    return text.strip()
