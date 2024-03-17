from flask import Flask, render_template, request
import PyPDF2
from difflib import SequenceMatcher

app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        for page in range(num_pages):
            text += reader.pages[page].extract_text()
    return text

def text_similarity(text1, text2):
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio() * 100

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']
        if file1 and file2:
            file1_content = file1.read()
            file2_content = file2.read()
            with open('file1.pdf', 'wb') as f1, open('file2.pdf', 'wb') as f2:
                f1.write(file1_content)
                f2.write(file2_content)
            
            text1 = extract_text_from_pdf('file1.pdf')
            text2 = extract_text_from_pdf('file2.pdf')
            similarity_percentage = text_similarity(text1, text2)

            if similarity_percentage > 90:
                message = "Malpractice detected! The similarity between the documents is above 90%."
            else:
                message = "No malpractice detected. The similarity between the documents is within acceptable limits."
            return render_template('index.html', message=message)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
