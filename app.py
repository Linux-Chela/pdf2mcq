from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import google.generativeai as genai
import PyPDF2
import os
from datetime import datetime

# Configure API key for Google Generative AI
os.environ["API_KEY"] = "AIzaSyDbHHc0S4mEKQ3NcX2xSBmzS1Zcp0ONgGg"
genai.configure(api_key=os.environ["API_KEY"])

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def read_pdf_in_chunks(file_path, pages_per_chunk=3, max_chars=3000):
    text_chunks = []
    with open(file_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for start in range(0, len(pdf_reader.pages), pages_per_chunk):
            chunk = ""
            for page_num in range(start, min(start + pages_per_chunk, len(pdf_reader.pages))):
                chunk += pdf_reader.pages[page_num].extract_text()
                if len(chunk) >= max_chars:  # Split chunk if it exceeds the limit
                    text_chunks.append(chunk[:max_chars])
                    chunk = chunk[max_chars:]
            if chunk:  # Add remaining chunk
                text_chunks.append(chunk)
    return text_chunks


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "pdf_file" not in request.files:
            return "No file part", 400

        file = request.files["pdf_file"]

        if file.filename == "":
            return "No selected file", 400

        # Save the uploaded PDF
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # Read the PDF content in chunks
        pdf_chunks = read_pdf_in_chunks(file_path)

        # Initialize the Generative Model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Process chunks in batches to optimize memory usage
        responses = []
        batch_size = 5  # Number of chunks to process in a single batch
        for batch_start in range(0, len(pdf_chunks), batch_size):
            batch = pdf_chunks[batch_start:batch_start + batch_size]
            for chunk in batch:
                try:
                    # Generate MCQs for the chunk
                    prompt = (
                        f"Document Content:\n{chunk}...\n\n"
                        "Create multiple-choice questions (MCQs) as much as possible from each sentence of the content. "
                        "Format should contain only three things mention below:\n"
                        "Question number) Question....\n"
                        "List options for each question (a, b, c, d).\n"
                        "Write the correct answer after each question in the format like 'Answer: (b)'."
                    )
                    response = model.generate_content(prompt)
                    responses.append(response.text)
                except Exception as e:
                    # Log and skip errors for individual chunks
                    print(f"Error processing chunk: {e}")
                    responses.append(f"Error processing chunk: {e}")

        # Save responses to a file (optional)
        output_file = os.path.join(app.config["UPLOAD_FOLDER"], "output.txt")
        with open(output_file, "w") as f:
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Report generated on: {current_datetime}\n\n")
            for response in responses:
                f.write(response + "\n\n")

        return render_template("results.html", responses=responses)

    return render_template("index.html")



@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
