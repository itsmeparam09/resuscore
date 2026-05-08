import streamlit as st
import test
from google.genai import errors
import os

# Load API keys
def get_api_keys():
    keys = []
    for i in range(1, 6):
        key = st.secrets.get(f"GEMINI_API_KEY_{i}") or os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
    return keys

if "api_key_index" not in st.session_state:
    st.session_state.api_key_index = 0

if "api_keys" not in st.session_state:
    st.session_state.api_keys = get_api_keys()

if "api_key" not in st.session_state:
    st.session_state.api_key = st.session_state.api_keys[0]

api_key = st.session_state.api_key

if "generate_page" not in st.session_state:
    st.session_state.generate_page = "CoverUploadPage"

# ─────────────────────────────────────────────
# PAGE 1 — Cover Letter Upload
# ─────────────────────────────────────────────
if st.session_state.generate_page == "CoverUploadPage":
    left, right = st.columns(spec=2, gap='medium', border=True)

    with right:
        st.header(body="Paste The Job Description Below", text_alignment="center")
        job_description = st.text_area(
            label="Paste the Job Description",
            height=500,
            label_visibility="collapsed",
            key="generate_desc"
        )

    with left:
        st.header(body="Drop Your Resume!", text_alignment="center")
        resume = st.file_uploader(
            label="Upload a Resume!",
            accept_multiple_files=False,
            label_visibility="collapsed",
            type=["pdf"],
            key="generate_resume"
        )

        st.container(height=100, border=False)
        left_space, btn_col, right_space = st.columns([1, 1, 1])

        with btn_col:
            if st.button("Generate Cover Letter", type="primary"):
                if resume is None or job_description.strip() == "":
                    st.warning("Please paste a job description and upload a resume first!")
                else:
                    st.session_state.generate_page = "loading"
                    st.session_state.resume = resume
                    st.session_state.job_description = job_description
                    st.rerun(scope="app")


# ─────────────────────────────────────────────
# PAGE 2 — Loading
# ─────────────────────────────────────────────
elif st.session_state.generate_page == "loading":
    st.title(body="Generating Your Cover Letter...")

    with st.spinner("Generating your cover letter..."):
        try:
            letter = test.writeLetter(
                api_key,
                st.session_state.job_description,
                st.session_state.resume,
            )
            st.session_state.letter = letter
            st.session_state.generate_page = "results"
            st.rerun(scope="app")
        except errors.ClientError as e: 
            if e.status_code == 429:
                next_index = st.session_state.api_key_index + 1
                if next_index < len(st.session_state.api_keys):
                    st.session_state.api_key_index = next_index
                    st.session_state.api_key = st.session_state.api_keys[next_index]
                    st.rerun(scope="app")  # retry automatically with next key
                else:
                    st.error("⚠️ All API keys have hit their rate limit. Please wait a few minutes and try again.")
                    if st.button("Go back"):
                        st.session_state.api_key_index = 0  # reset for next time
                        st.session_state.resume_page = "CoverUploadPage"
                        st.rerun(scope="app")
            elif e.status_code == 403:
                st.error("⚠️ Invalid API key. Please check your .env file.")
            elif e.status_code == 500:
                st.error("⚠️ Google's servers are having issues. Please try again.")
            else:
                st.error(f"⚠️ Something went wrong ({e.status_code}). Please try again.")
            
            if st.button("Go back"):
                st.session_state.resume_page = "CoverUploadPage"
                st.rerun(scope="app")


# ─────────────────────────────────────────────
# PAGE 3 — Results
# ─────────────────────────────────────────────
elif st.session_state.generate_page == "results":
    st.markdown("## Your Generated Cover Letter")
    st.markdown("---")

    letter = st.session_state.letter

    # Header info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Candidate:** {letter.get('candidate_name', '')}")
    with col2:
        st.markdown(f"**Role:** {letter.get('job_title', '')}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Cover letter text in scrollable container
    with st.container(height=500, border=True):
        st.write(letter.get("cover_letter", ""))

    st.markdown("---")

    # Copy-friendly text area
    st.text_area(
        label="Copy your cover letter",
        value=letter.get("cover_letter", ""),
        height=300,
        key="copy_letter"
    )

    if st.button("Generate another cover letter"):
        st.session_state.generate_page = "CoverUploadPage"
        st.rerun(scope="app")
