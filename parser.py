from typing import TextIO
import pdfplumber as pp
import streamlit as st
import os
import io
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY_1")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY_1")

api_key = get_api_key()

file = "Param Khurana Resume New Final.pdf"
def extract_text(file: TextIO):
    text = " "
    try:
        with pp.open(io.BytesIO(file.read())) as f:
            for page in f.pages:
                contents = page.extract_text()
                text+=contents + "\n"
            return text
    except FileNotFoundError:
        print("file unsupported")

    








    