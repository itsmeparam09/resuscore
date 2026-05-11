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


if "resume_page" not in st.session_state:
    st.session_state.resume_page = "ResumeUploadPage"
# ─────────────────────────────────────────────
# Helper Functions 
# ─────────────────────────────────────────────

def score_color(score: int) -> str:
    """Return a hex color based on score value."""
    if score >= 75:
        return "#639922"   # green
    elif score >= 50:
        return "#EF9F27"   # amber
    else:
        return "#E24B4A"   # red


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
        rotation=-90,  # ← start from top instead of right
    )])

    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),  # ← give it breathing room
        width=size,
        height=size,
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
    """
    Safely extracts each feedback section from the dictionary
    returned by Gemini.  Returns a dict with clean lists/items
    so the UI never crashes on missing keys.
    """
    return {
        "strengths":        feedback.get("strengths", []),
        "weaknesses":       feedback.get("weaknesses", []),
        "missing_keywords": feedback.get("missing_keywords", []),
        "improvements":     feedback.get("improvements", []),
    }


def extract_score_sections(score: dict) -> dict:
    """
    Safely extracts every score field returned by the scoring prompt.
    Returns sensible defaults (0) so charts never crash on missing keys.
    """
    return {
        "overall_score":  score.get("overall_score",  0),
        "keyword_match":  score.get("keyword_match",  0),
        "relevance":      score.get("relevance",      0),
        "structure":      score.get("structure",      0),
        "impact":         score.get("impact",         0),
    }


# ─────────────────────────────────────────────
# PAGE 1 — Resume Upload
# ─────────────────────────────────────────────
if st.session_state.resume_page == "ResumeUploadPage":
    left, right = st.columns(spec=2, gap='medium', border=True)

    with right:
        st.header(body="Paste The Job Description Below", text_alignment="center")
        job_description = st.text_area(
            label="Paste the Job Description",
            height=500,
            label_visibility="collapsed",
            key="resume_desc"
        )

    with left:
        st.header(body="Drop Your Resume!", text_alignment="center")
        resume = st.file_uploader(
            label="Upload a resume!",
            accept_multiple_files=False,
            label_visibility="collapsed"
        )

        st.container(height=100, border=False)
        left_space, btn_col, right_space = st.columns([1, 1, 1])

        with btn_col:
            if st.button("Score My Resume", type="primary"):
                if resume is None or job_description.strip() == "":
                    st.warning("Please paste a job description and upload a resume first!")
                else:
                    st.session_state.resume_page = "loading"
                    st.session_state.resume = resume
                    st.session_state.job_description = job_description
                    st.rerun(scope="app")



# ─────────────────────────────────────────────
# PAGE 2 — Loading
# ─────────────────────────────────────────────
elif st.session_state.resume_page == "loading":
    st.title(body="Analyzing Your Resume...")

    with st.spinner("Analyzing your resume..."):
        try:

            feedback = test.ResumeScoreAndFeedback(api_key, st.session_state.job_description, st.session_state.resume)
            score = API_calls.ScoreResume(api_key, st.session_state.resume, st.session_state.job_description)

            st.session_state.feedback = feedback
            st.session_state.score = score
    
            st.session_state.resume_page = "results"
            st.rerun(scope="app")
        except errors.ClientError as e:
            code = getattr(e, 'code', None) or getattr(e, 'status_code', None)
            error_str = str(e)
    
            if code == 429 or '429' in error_str:
                next_index = st.session_state.api_key_index + 1
                if next_index < len(st.session_state.api_keys):
                    st.session_state.api_key_index = next_index
                    st.session_state.api_key = st.session_state.api_keys[next_index]
                    st.rerun(scope="app")
                else:
                    st.error("⚠️ All API keys have hit their rate limit. Please wait a few minutes and try again.")
                    if st.button("Go back"):
                        st.session_state.api_key_index = 0
                        st.session_state.generate_page = "CoverUploadPage"
                        st.rerun(scope="app")
            elif code == 403 or '403' in error_str:
                st.error("⚠️ Invalid API key. Please check your API key.")
            elif code == 500 or '500' in error_str:
                st.error("⚠️ Google's servers are having issues. Please try again.")
            else:
                st.error(f"⚠️ Something went wrong. Please try again. Details: {error_str}")
            
            if st.button("Go back"):
                st.session_state.resume_page = "ResumeUploadPage"
                st.rerun(scope="app")


# ─────────────────────────────────────────────
# PAGE 3 — Results
# ─────────────────────────────────────────────
elif st.session_state.resume_page == "results":

    s = extract_score_sections(st.session_state.score)
    f = extract_feedback_sections(st.session_state.feedback)

    st.markdown("## Your results")
    st.markdown("---")

    left_col, right_col = st.columns(2, gap="medium")

    # ── LEFT COLUMN — scrollable feedback ────────────────────────────────────
    with left_col:
        st.markdown("#### Feedback")

        # Streamlit does not have a native scroll container so we use
        # st.container() combined with a fixed-height div via markdown.
        # All four sections sit inside one scrollable area.
        scroll_html = '<div style="height:560px;overflow-y:auto;padding-right:6px;">'

        # 1. Strengths
        scroll_html += '<p style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#3B6D11;margin:0 0 6px;">Strengths</p>'
        for item in f["strengths"]:
            scroll_html += f'<div style="font-size:13px;padding:7px 10px;border-radius:8px;background:#EAF3DE;border-left:2px solid #639922;margin-bottom:6px;line-height:1.5;">{item}</div>'

        # 2. Weaknesses
        scroll_html += '<p style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#BA7517;margin:16px 0 6px;">Weaknesses</p>'
        for item in f["weaknesses"]:
            scroll_html += f'<div style="font-size:13px;padding:7px 10px;border-radius:8px;background:#FAEEDA;border-left:2px solid #EF9F27;margin-bottom:6px;line-height:1.5;">{item}</div>'

        # 3. Missing keywords
        scroll_html += '<p style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:#185FA5;margin:16px 0 6px;">Missing keywords</p>'
        for item in f["missing_keywords"]:
            scroll_html += f'<div style="font-size:13px;padding:7px 10px;border-radius:8px;background:#E6F1FB;border-left:2px solid #378ADD;margin-bottom:6px;line-height:1.5;">{item}</div>'

        # 4. Corrections (before / after)
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

    # ── RIGHT COLUMN — score circles ──────────────────────────────────────────
    with right_col:
        st.markdown("#### Score breakdown")

        # Big overall score circle — centered
        center_col = st.columns([1, 2, 1])[1]
        with center_col:
            st.plotly_chart(
                make_circle(s["overall_score"], size=180),
                use_container_width=False,
                config={"displayModeBar": False},
                key = "Overall score chart"
            )
            st.markdown(
                '<p style="text-align:center;font-size:12px;color:gray;margin-top:-12px;">Overall score</p>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Four small circles in a 2x2 grid
        small_scores = [
            ("Keyword match", s["keyword_match"]),
            ("Relevance",     s["relevance"]),
            ("Structure",     s["structure"]),
            ("Impact",        s["impact"]),
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
                    key = f'small circle {i}'
                )
                st.markdown(
                    f'<p style="text-align:center;font-size:11px;color:black;margin-top:-14px;">{label}</p>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # Back button
    if st.button("Score another resume"):
        st.session_state.resume_page = "home"
        st.rerun(scope="app")

