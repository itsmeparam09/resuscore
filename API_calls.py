from google import genai
from dotenv import load_dotenv
import os
from google.genai import types
import json
import streamlit as st
import re

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



def ValidateJSON(api_key, text):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents= f"""Take the string: {text} and convert it to valid JSON object such that it could be converted to a python dictionary
    Return ONLY a valid JSON object. No markdown, no code fences, 
    no explanation. Start your response with '{' and end with '}'."""
    )
    return response.text

def cleanJSON(text):
    
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        fixed = ValidateJSON(api_key, text)
        fixed = fixed.strip()
        fixed = re.sub(r'^```(?:json)?\s*', '', fixed)
        fixed = re.sub(r'\s*```$', '', fixed)
        start = fixed.find('{')
        end = fixed.rfind('}')
        if start != -1 and end != -1:
            fixed = fixed[start:end+1]
        return json.loads(fixed)
    except Exception:
        return {}

def ConvertResumeToDict(api_key, text):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents= f"Extract all the information from the given messy text that is generated from a resume and return the extracted and arranges data in JSON. Do not write json at the end or beggining and give me clean text ready to convert to string.: {text}"
    )
    cleaned_text = cleanJSON(response.text)
    return cleaned_text


def ScoreResume(api_key, resume, job_description):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f'''You are an expert recruiter with 10 years of experience hiring across multiple industries.
        You will be given a resume and a job description. Your job is to score the resume against the job description.

        RESUME:
        {resume}

        JOB DESCRIPTION:
        {job_description}

        Score the resume across these 5 dimensions on a scale of 0 to 100.
        Use this rubric strictly for every dimension:

        90-100: Exceptional. Exceeds all requirements. Every element is present, specific, and impactful.
        70-89:  Strong. Meets most requirements with minor gaps.
        50-69:  Average. Meets some requirements but has clear gaps.
        30-49:  Weak. Meets few requirements. Significant gaps present.
        0-29:   Poor. Does not meet the requirements for this dimension.

        DIMENSIONS:
        1. Keyword Match — what percentage of the important keywords from the job description appear in the resume?
            Score based on: 90+ keywords = 90-100, 70-89% keywords = 70-89, and so on.

        2. Relevance — how directly does the candidate experience match this specific role?
            Score based on: directly relevant experience = 70+, tangentially relevant = 50-69, irrelevant = below 50.

        3. Structure — does the resume have all required sections?
             Score based on: all 4 sections present and well formatted = 80+, missing 1 section = 60-79, missing 2+ = below 60.
            Required sections: contact info, work experience, education, skills.

        4. Impact — what percentage of bullet points show measurable achievements vs just listing responsibilities?
            Score based on: 80%+ bullets have metrics = 80+, 50-79% have metrics = 50-79, below 50% = below 50.

        5. Context — are skills and experiences described with strong specific context or stated vaguely?
            Score based on: all entries have specific context = 80+, some vague entries = 50-79, mostly vague = below 50.

        Give less weightage to preferred qualifications when scoring keyword match.
            Do not use any markdown formatting. No bold, no italics, no asterisks.''',
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "overall_score":    {"type": "integer"},
                    "keyword_match":    {"type": "integer"},
                    "relevance":        {"type": "integer"},
                    "structure":        {"type": "integer"},
                    "impact":           {"type": "integer"},
                    "missing_keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["overall_score", "keyword_match", "relevance", "structure", "impact", "missing_keywords"]
            }
        )
    )
    return json.loads(response.text)



def ResumeFeedback(api_key, score, resume, job_description):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"""You are a hiring manager with 10+ years of experience across multiple industries.
You will be given a resume, a job description, and an overall resume score.
Your job is to provide detailed, human-sounding, personalized feedback based on these inputs.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

SCORE:
{score}

The feedback must cover these 4 components:
1. Strengths — what the candidate does well relative to this role
2. Weaknesses — specific gaps between the resume and job description
3. Missing Keywords — how to naturally incorporate missing keywords into the resume
4. Improvements — 3 specific bullet point rewrites showing before and after to demonstrate impact

Do not use any markdown formatting. No bold, no italics, no asterisks.
The provided feedback should not be more than 900 words.""",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "strengths":        {"type": "array", "items": {"type": "string"}},
                    "weaknesses":       {"type": "array", "items": {"type": "string"}},
                    "missing_keywords": {"type": "array", "items": {"type": "string"}},
                    "improvements": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "before": {"type": "string"},
                                "after":  {"type": "string"},
                                "reason": {"type": "string"}
                            },
                            "required": ["before", "after", "reason"]
                        }
                    }
                },
                "required": ["strengths", "weaknesses", "missing_keywords", "improvements"]
            }
        )
    )
    return json.loads(response.text)




def ScoreLetter(api_key, cover_letter, job_description):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f'''You are an expert recruiter with 10+ years of experience hiring
across multiple industries.
You will be given a cover letter and a job description.
Your job is to score the cover letter against the job description.

COVER LETTER:
{cover_letter}

JOB DESCRIPTION:
{job_description}

Score the cover letter across these 4 dimensions:
1. Personalization — does the cover letter feel tailored to this specific role and company or does it feel generic?
2. Relevance — does the candidate connect their experience to the specific requirements of this job?
3. Tone — is the writing professional, confident, and appropriate for the industry?
4. Structure — does it have a strong opening, a clear middle that sells the candidate, and a call to action closing?

Do not use any markdown formatting. No bold, no italics, no asterisks.''',
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "overall_score":    {"type": "integer"},
                    "personalization":  {"type": "integer"},
                    "relevance":        {"type": "integer"},
                    "tone":             {"type": "integer"},
                    "structure":        {"type": "integer"},
                    "missing_keywords": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["overall_score", "personalization", "relevance", "tone", "structure", "missing_keywords"]
            }
        )
    )
    return json.loads(response.text)


def GenereateLetter(api_key, resume, job_description):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f'''You are an expert career coach and professional writer with 10+ years of experience
crafting cover letters that get candidates hired across multiple industries.
You will be given a resume and a job description.
Your job is to write a personalized, professional cover letter tailored specifically to this role.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

When writing the cover letter:
- Extract the candidate name, most relevant experience, and strongest skills directly from the resume
- Reference specific requirements, responsibilities, and keywords from the job description naturally throughout the letter
- Do not invent any experience, skills, or achievements that are not present in the resume
- Do not use generic phrases like "I am a hard worker" or "I am passionate about" — every sentence must be specific and backed by the resume

The cover letter must follow this exact structure:
- Paragraph 1: Strong opening that mentions the specific role, where the candidate found it, and one compelling reason why they are a strong fit based on their most relevant experience
- Paragraph 2: Connect 2 to 3 specific experiences or achievements from the resume directly to the key requirements of the job description
- Paragraph 3: Brief closing that expresses genuine interest in the specific company, includes a call to action, and ends professionally

Do not use any markdown formatting. No bold, no italics, no asterisks.''',
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "candidate_name": {"type": "string"},
                    "job_title":      {"type": "string"},
                    "cover_letter":   {"type": "string"}
                },
                "required": ["candidate_name", "job_title", "cover_letter"]
            }
        )
    )
    return json.loads(response.text)


