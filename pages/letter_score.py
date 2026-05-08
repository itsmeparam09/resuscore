import streamlit as st
import test
import API_calls
import plotly.graph_objects as go
import os
from google.genai import errors

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


if "letter_page" not in st.session_state:
    st.session_state.letter_page = "LetterUploadPage"

# ─────────────────────────────────────────────
# Helper Functions 
# ─────────────────────────────────────────────

def score_color(score: int) -> str:
    if score >= 75:
        return "#639922"
    elif score >= 50:
        return "#EF9F27"
    else:
        return "#E24B4A"

def make_circle(score: int, size: int = 200) -> go.Figure:
    color = score_color(score)
    remaining = 100 - score
    fig = go.Figure(data=[go.Pie(
        values=[score, remaining],
        hole=0.65,
        marker_colors=[color, "rgba(200,200,200,0.15)"],
        textinfo="none",
        hoverinfo="none",
        sort=False,
        direction="clockwise",
        rotation=-90,
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        width=size, height=size,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{score}</b>",
            x=0.5, y=0.5,
            font=dict(size=size // 6, color="#1a1a1a"),
            showarrow=False,
        )],
    )
    return fig

def extract_feedback_sections(feedback: dict) -> dict:
    return {
        "strengths":        feedback.get("strengths", []),
        "weaknesses":       feedback.get("weaknesses", []),
        "missing_keywords": feedback.get("missing_keywords", []),
        "improvements":     feedback.get("improvements", []),
    }

def extract_score_sections(score: dict) -> dict:
    return {
        "overall_score":    score.get("overall_score",    0),
        "personalization":  score.get("personalization",  0),
        "relevance":        score.get("relevance",        0),
        "tone":             score.get("tone",             0),
        "structure":        score.get("structure",        0),
    }

# ─────────────────────────────────────────────
# PAGE 1 — Cover Letter Upload
# ─────────────────────────────────────────────
if st.session_state.letter_page == "LetterUploadPage":
    left, right = st.columns(spec=2, gap='medium', border=True)

    with right:
        st.header(body="Paste The Job Description Below", text_alignment="center")
        job_description = st.text_area(
            label="Paste the Job Description",
            height=500,
            label_visibility="collapsed",
            key="letter_desc"
        )

    with left:
        st.subheader(body="Drop Your Resume!", text_alignment="center")
        resume = st.file_uploader(
            label="Upload a resume!",
            accept_multiple_files=False,
            label_visibility="collapsed",
            type=["pdf"],
            key="resume_uploader"
        )

        st.container(height=200, border=False)
        st.subheader(body="Drop your Cover Letter!", text_alignment="center")
        letter = st.file_uploader(
            label="Upload a Cover Letter!",
            accept_multiple_files=False,
            label_visibility="collapsed",
            type=["pdf"],
            key="letter_uploader"
        )

    left_space, btn_col, right_space = st.columns([1, 1, 1])
    with btn_col:
        if st.button("Score My Cover Letter", type="primary"):
            if resume is None or letter is None or job_description.strip() == "":
                st.warning("Please upload both files and paste a job description first!")
            else:
                st.session_state.letter_page = "loading"
                st.session_state.resume = resume
                st.session_state.letter = letter
                st.session_state.job_description = job_description
                st.rerun(scope="app")


# ─────────────────────────────────────────────
# PAGE 2 — Loading
# ─────────────────────────────────────────────
elif st.session_state.letter_page == "loading":
    st.title(body="Analyzing Your Cover Letter...")

    with st.spinner("Analyzing your cover letter..."):
        try:
            score, feedback = test.LetterScoreAndFeedback(
                api_key,
                st.session_state.job_description,
                st.session_state.letter,
                st.session_state.resume
            )
            st.session_state.feedback = feedback
            st.session_state.score = score
            st.session_state.letter_page = "results"
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
                        st.session_state.resume_page = "LetterUploadPage"
                        st.rerun(scope="app")
            elif e.status_code == 403:
                st.error("⚠️ Invalid API key. Please check your .env file.")
            elif e.status_code == 500:
                st.error("⚠️ Google's servers are having issues. Please try again.")
            else:
                st.error(f"⚠️ Something went wrong ({e.status_code}). Please try again.")
            
            if st.button("Go back"):
                st.session_state.resume_page = "LetterUploadPage"
                st.rerun(scope="app")



# ─────────────────────────────────────────────
# PAGE 3 — Results
# ─────────────────────────────────────────────
elif st.session_state.letter_page == "results":

    s = extract_score_sections(st.session_state.score)
    f = extract_feedback_sections(st.session_state.feedback)

    st.markdown("## Your results")
    st.markdown("---")

    left_col, right_col = st.columns(2, gap="medium")

    with left_col:
        st.markdown("#### Feedback")
        scroll_html = '<div style="height:560px;overflow-y:auto;padding-right:6px;">'

        scroll_html += '<p style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#3B6D11;margin:0 0 6px;">Strengths</p>'
        for item in f["strengths"]:
            scroll_html += f'<div style="font-size:13px;padding:7px 10px;border-radius:8px;background:#EAF3DE;border-left:2px solid #639922;margin-bottom:6px;line-height:1.5;">{item}</div>'

        scroll_html += '<p style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#BA7517;margin:16px 0 6px;">Weaknesses</p>'
        for item in f["weaknesses"]:
            scroll_html += f'<div style="font-size:13px;padding:7px 10px;border-radius:8px;background:#FAEEDA;border-left:2px solid #EF9F27;margin-bottom:6px;line-height:1.5;">{item}</div>'

        scroll_html += '<p style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#185FA5;margin:16px 0 6px;">Missing keywords</p>'
        for item in f["missing_keywords"]:
            scroll_html += f'<div style="font-size:13px;padding:7px 10px;border-radius:8px;background:#E6F1FB;border-left:2px solid #378ADD;margin-bottom:6px;line-height:1.5;">{item}</div>'

        scroll_html += '<p style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#993556;margin:16px 0 6px;">Corrections</p>'
        for imp in f["improvements"]:
            before = imp.get("before", "")
            after  = imp.get("after",  "")
            reason = imp.get("reason", "")
            scroll_html += f'''
            <div style="background:#f8f8f8;border-radius:8px;padding:10px 12px;margin-bottom:10px;">
                <p style="font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#A32D2D;margin:0 0 3px;">Before</p>
                <p style="font-size:12px;margin:0 0 8px;line-height:1.5;">{before}</p>
                <p style="font-size:10px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#3B6D11;margin:0 0 3px;">After</p>
                <p style="font-size:12px;margin:0 0 6px;line-height:1.5;">{after}</p>
                <p style="font-size:11px;color:#888;font-style:italic;margin:0;">{reason}</p>
            </div>'''

        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)

    with right_col:
        st.markdown("#### Score breakdown")

        center_col = st.columns([1, 2, 1])[1]
        with center_col:
            st.plotly_chart(
                make_circle(s["overall_score"], size=180),
                use_container_width=False,
                config={"displayModeBar": False},
                key="letter_overall_score_chart"
            )
            st.markdown(
                '<p style="text-align:center;font-size:12px;color:gray;margin-top:-12px;">Overall score</p>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        small_scores = [
            ("Personalization", s["personalization"]),
            ("Relevance",       s["relevance"]),
            ("Structure",       s["structure"]),
            ("Tone",            s["tone"]),
        ]

        row1, row2 = st.columns(2), st.columns(2)
        rows = [row1, row2]

        for i, (label, val) in enumerate(small_scores):
            row_idx = i // 2
            col_idx = i % 2
            with rows[row_idx][col_idx]:
                st.plotly_chart(
                    make_circle(val, size=120),
                    use_container_width=False,
                    config={"displayModeBar": False},
                    key=f"letter_small_circle_{i}"
                )
                st.markdown(
                    f'<p style="text-align:center;font-size:11px;color:black;margin-top:-14px;">{label}</p>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    if st.button("Score another cover letter"):
        st.session_state.letter_page = "LetterUploadPage"
        st.rerun(scope="app")
