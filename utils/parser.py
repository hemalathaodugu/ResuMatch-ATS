import PyPDF2
from docx import Document


def extract_pdf_text(file_path):

    text = ""

    pdf = PyPDF2.PdfReader(file_path)

    for page in pdf.pages:
        text += page.extract_text()

    return text



def extract_docx_text(file_path):

    doc = Document(file_path)

    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text

    return text