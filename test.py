import API_calls
import parser
import streamlit as st
import os
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


def ResumeScoreAndFeedback(api_key, job_description, resume):
    RawResume = parser.extract_text(resume)
    resume_dict = API_calls.ConvertResumeToDict(api_key, RawResume)
    ResumeScore = API_calls.ScoreResume(api_key, resume_dict, job_description)
    ResumeFeedback = API_calls.ResumeFeedback(api_key, ResumeScore, resume_dict, job_description)
    return ResumeFeedback
    

def LetterScoreAndFeedback(api_key, job_description, cover_letter, resume):
    RawResume = parser.extract_text(resume)
    resume_dict = API_calls.ConvertResumeToDict(api_key, RawResume)
    LetterText = parser.extract_text(cover_letter)
    LetterScore = API_calls.ScoreLetter(api_key, LetterText, job_description)
    LetterFeedback = API_calls.LetterFeedback(api_key, LetterText, job_description, resume_dict, LetterScore)
    return LetterScore, LetterFeedback

def catagorizeFeeedback(text):
    strengths = text["strengths"]
    weaknesses = text["weaknesses"]
    missing_keywords_desc = text["missing_keywords"]
    improvements = text["improvements"]
    return strengths, weaknesses, missing_keywords_desc, improvements

def catagorizeScore(text):
    overall_score = text["overall_score"]
    keyword_match = text["keyword_match"]
    relevance = text["relevance"]
    structure = text["structure"]
    impact = text["impact"]
    missing_keywords = text["missing_keywords"]
    return overall_score, keyword_match, relevance, structure, impact, missing_keywords

def writeLetter(api_key, job_description, resume):
    resume_string = parser.extract_text(resume)
    letter = API_calls.GenereateLetter(api_key, resume_string, job_description)
    return letter
