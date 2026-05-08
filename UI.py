import streamlit as st

st.set_page_config(layout="wide")

# Initialize ALL session state here once, before navigation
if "resume_page" not in st.session_state:
    st.session_state.resume_page = "ResumeUploadPage"

if "letter_page" not in st.session_state:
    st.session_state.letter_page = "LetterUploadPage"

if "generate_page" not in st.session_state:
    st.session_state.generate_page = "CoverUploadPage"

resume_page = st.Page("pages/resume.py", title="Score Resume", icon="📄")
letter_score_page = st.Page("pages/letter_score.py", title="Score Cover Letter", icon="✉️")
generate_page = st.Page("pages/generate_letter.py", title="Generate Cover Letter", icon="✍️")

pg = st.navigation({
    "Resume": [resume_page],
    "Cover Letter": [letter_score_page, generate_page]
})
pg.run()