import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

client = genai.Client(api_key=api_key)

if not api_key:
    st.error("API key not found. Please set it in your .env file.")
    st.stop()

st.set_page_config(page_title = "Document Question AI", layout = "centered")

st.title("📄 Document Question AI")
st.write("Upload a document and ask questions about it.")

uploaded_file = st.file_uploader(
    "Upload document (PDF, DOCX, TXT)",
    type = ["pdf", "docx", "txt"]
)

def read_document(file): 

    if file.type == "application/pdf":
        pdf = PdfReader(file)
        text = ""

        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file.type == "text/plain":
        return str(file.read(), "utf-8")

    return ""

def split_text(text, size=800):

    chunks = []
    start = 0

    while start < len(text):
        chunks.append(text[start:start+size])
        start += size

    return chunks

if uploaded_file:

    text = read_document(uploaded_file)

    chunks = split_text(text)

    st.success("Document uploaded successfully!")

    question = st.text_input(
        "Ask a question about the document:",
        placeholder="Example: Who is the author?"
    )

    if question:

        question_words = question.lower().split()

        for chunk in chunks:
            score = sum(word in chunk.lower() for word in question_words)
                if score > 0:
                    relevant_chunks.append((score, chunk))

        relevant_chunks = sorted(relevant_chunks, reverse=True)
        context = " ".join([chunk for _, chunk in relevant_chunks[:3]])

        prompt = f"""
        Use the following document context to answer the question.

        Context:
        {context}

        Question:
        {question}
        """
        with st.spinner("Thinking... 🤔"):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        st.subheader("Answer")
        st.write(response.text)