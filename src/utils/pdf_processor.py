import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    """
    Verilen PDF dosyasindan metin icerigini cikarir.
    """
    text_content = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content += text + "\n"
        return text_content
    except Exception as e:
        return f"Error reading PDF: {str(e)}"