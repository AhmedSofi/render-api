from fastapi import FastAPI, File, UploadFile, Response
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import re
from fastapi import FastAPI, Query

import google.generativeai as genai
app = FastAPI()


def gemini(question_and_answer: str):
    genai.configure(api_key='AIzaSyAFAmVIP6l33PQUj5G0Yk05RyH9u42g1gg')
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        f'Describe each question and its answer, and provide information about the question and answer, treatment methods, if any, and whether it requires consulting a doctor or not. ' + question_and_answer)

    return response.text
def format_text_for_pdf(input_string):
    formatted_string = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', input_string)
    formatted_string = re.sub(r'\*(.*?)\*', r'<font color="darkgrey">\1</font>', formatted_string)
    formatted_string = formatted_string.replace('*', '')
    formatted_string = formatted_string.replace('\n\n', '\n\n')
    formatted_string = formatted_string.replace('\n', '\n')
    return formatted_string


def create_pdf(input_string, output_file):
    formatted_text = format_text_for_pdf(input_string)

    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        name='Custom',
        parent=styles['BodyText'],
        leading=14,
        spaceAfter=10,
    )

    story = []

    for part in formatted_text.split('\n'):
        if part.strip():
            paragraph = Paragraph(part, custom_style)
            story.append(paragraph)
            story.append(Spacer(1, 12))

    doc.build(story)


@app.post("/generate_pdf/")
async def generate_pdf(question: list = Query(...), answer: list = Query(...)):
    cu = 1
    question_and_answer = ""
    for i in range(len(question)):
        question_and_answer += "Q{cu}: {q} A{cu}: {a} ".format(cu=cu, q=question[i], a=answer[i])
        cu += 1
    output_file = "output.pdf"
    input_string = gemini(question_and_answer)
    create_pdf(input_string, output_file)
    with open(output_file, 'rb') as f:
        pdf_content = f.read()
    return Response(content=pdf_content, media_type='application/pdf', headers={'Content-Disposition': 'attachment; filename="output.pdf"'})
@app.get("/")
async def read_root():
    return {"Hello": "sofi770"}
