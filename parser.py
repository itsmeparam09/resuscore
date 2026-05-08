import json
from typing import TextIO
import pdfplumber as pp
import API_calls
import io
api_key = API_calls.api_key
file = "Param Khurana Resume New Final.pdf"
def extract_text(file: TextIO):
    text = " "
    try:
        with pp.open(file) as f:
            for page in f.pages:
                contents = page.extract_text()
                text+=contents + "\n"
            return text
    except FileNotFoundError:
        print("file unsupported")

    








    