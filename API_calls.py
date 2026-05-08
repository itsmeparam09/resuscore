from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def ValidateJSON(api_key, text):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents= f"""Take the string: {text} and convert it to valid JSON object such that it could be converted to a python dictionary"""
    )
    return response.text

def cleanJSON(cleaned_txt):
    if cleaned_txt.startswith("```json"):
        cleaned_txt = cleaned_txt[8:]
    elif cleaned_txt.startswith("```"):
        cleaned_txt = cleaned_txt[3:]
    elif cleaned_txt.startswith("json"):
        cleaned_txt = cleaned_txt[5:]
    if cleaned_txt.endswith("```"):
        cleaned_txt = cleaned_txt[:-3]
    cleaned_txt = cleaned_txt.strip()
    try:
        data = json.loads(cleaned_txt)
    except json.JSONDecodeError:
        dataJSON = ValidateJSON(api_key, cleaned_txt)
        data = json.loads(dataJSON)
    return data

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
    contents= f'''You are an expert recruiter with 10 years of experience hiring across multiple industries. 
    You will be given a resume and a job description. Your job is to score the resume against the job description. 
    RESUME: {resume} 
    JOB DESCRIPTION:{job_description} 
    Score the resume across these 4 dimensions: 
    1. Keyword Match — do the resume skills and experience match the keywords in the job description? 
    2. Relevance — is the candidate's background relevant to this specific role? 
    3. Structure — does the resume have all necessary sections: experience, education, skills, and contact info? 
    4. Impact — do bullet points show achievements and results, not just responsibilities? 
    5. Context- are the words used in a strong and impactful context or just stated vaguely. 
    Return ONLY a JSON object in exactly this format, no extra text: 
    *Give less waithage to teh prefered qualifications section in the job description
    "overall_score": 78, "keyword_match": 80, "relevance": 75, "structure": 90, "impact": 65,"missing_keywords": ["keyword1", "keyword2", "keyword3"] 
    '''
    )
    cleaned_text = cleanJSON(response.text)
    return cleaned_text



def ResumeFeedback(api_key, score, resume, job_description):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents= f"""You are a hiring manager with 10+ years of experience across multiple industries. 
    You will be given a resume, a job description, and an overall resume score. Your job is to provide detailed, human-sounding, personalized feedback based on these inputs. 
    RESUME: {resume} 
    JOB DESCRIPTION: {job_description} 
    SCORE: {score} 
    The feedback must cover these 4 components: 
    1. Strengths — what the candidate does well relative to this role 
    2. Weaknesses — specific gaps between the resume and job description 
    3. Missing Keywords — how to naturally incorporate missing keywords into the resume 
    4. Improvements — 3 specific bullet point rewrites showing before and after to demonstrate impact 
    Return ONLY a JSON object in exactly this format, no extra text: 
    The provided feedback should not be more than 900 words.
    "strengths": ["strength 1", "strength 2", "strength 3"], "weaknesses": ["weakness 1", "weakness 2", "weakness 3"], "missing_keywords": ["how to include keyword 1", "how to include keyword 2"], "improvements": [  "before": "original bullet point from resume", "after": "improved version of that bullet point", "reason": "why this change makes it stronger"  ]"""
    )
    cleaned_text = cleanJSON(response.text)
    return cleaned_text





def ScoreLetter(api_key, cover_letter, job_description):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents= f'''You are an expert recruiter with 10+ years of experience hiring 
    across multiple industries.

    You will be given a cover letter and a job description. Your job 
    is to score the cover letter against the job description.

    COVER LETTER:
    {cover_letter}

    JOB DESCRIPTION:
    {job_description}

    Score the cover letter across these 4 dimensions:
    1. Personalization — does the cover letter feel tailored to this 
    specific role and company or does it feel generic?
    2. Relevance — does the candidate connect their experience to the 
    specific requirements of this job?
    3. Tone — is the writing professional, confident, and appropriate 
    for the industry?
    4. Structure — does it have a strong opening, a clear middle that 
    sells the candidate, and a call to action closing?

    Return ONLY a JSON object in exactly this format, no extra text:
    "overall_score": 78,
    "personalization": 80,
    "relevance": 75,
    "tone": 85,
    "structure": 70,
    "missing_keywords": ["keyword1", "keyword2", "keyword3"]
    '''
    )
    cleaned_text = cleanJSON(response.text)
    return cleaned_text


def LetterFeedback(api_key, cover_letter, job_description, resume, letter_score):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents= f'''You are a hiring manager with 10+ years of experience across 
    multiple industries.

    You will be given a cover letter, a job description, and a resume. 
    Your job is to provide detailed, human-sounding, personalized 
    feedback on the cover letter based on all three inputs.

    COVER LETTER:
    {cover_letter}

    JOB DESCRIPTION:
    {job_description}

    RESUME:
    {resume}

    COVER LETTER SCORE:
    {letter_score}

    When generating feedback, cross reference the cover letter with 
    the resume to:
    - Identify skills or experiences in the resume that are missing 
    from the cover letter and should be highlighted
    - Flag any claims in the cover letter that are not supported 
    by the resume
    - Point out any inconsistencies in dates, roles, or experience 
    between the two documents

    The feedback must cover these 4 components:
    1. Strengths — what the candidate does well in the cover letter 
    relative to this role
    2. Weaknesses — specific gaps or missed opportunities in the 
    cover letter
    3. Missing Keywords — how to naturally incorporate missing 
    keywords from the job description into the cover letter
    4. Improvements — 3 specific sentence rewrites showing before 
    and after to demonstrate impact

    The feedback must be personalized — reference specific lines 
    from the cover letter and specific requirements from the job 
    description. Do not give generic advice.

    Return ONLY a JSON object in exactly this format, no extra text:

     "strengths": ["strength 1", "strength 2", "strength 3"],
     "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
     "missing_keywords": ["how to include keyword 1", "how to include keyword 2"],
     "improvements": 
         "before": "original sentence from cover letter",
         "after": "improved version of that sentence",
         "reason": "why this change makes it stronger"
    '''
    )
    cleaned_text = cleanJSON(response.text)
    return cleaned_text


def GenereateLetter(api_key, resume, job_description):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents= f'''You are an expert career coach and professional writer with 10+ 
    years of experience crafting cover letters that get candidates 
    hired across multiple industries.

    You will be given a resume and a job description. Your job is to 
    write a personalized, professional cover letter tailored 
    specifically to this role.

    RESUME:
    {resume}

    JOB DESCRIPTION:
    {job_description}

    When writing the cover letter:
    - Extract the candidate's name, most relevant experience, and 
    strongest skills directly from the resume
    - Reference specific requirements, responsibilities, and keywords 
     from the job description naturally throughout the letter
    - Do not invent any experience, skills, or achievements that are 
      not present in the resume
    - Do not use generic phrases like "I am a hard worker" or 
     "I am passionate about" — every sentence must be specific 
     and backed by the resume

    The cover letter must follow this exact structure:
    - Paragraph 1: Strong opening that mentions the specific role, 
    where the candidate found it, and one compelling reason why 
    they are a strong fit based on their most relevant experience
    - Paragraph 2: Connect 2 to 3 specific experiences or 
    achievements from the resume directly to the key requirements 
    of the job description
    - Paragraph 3: Brief closing that expresses genuine interest in 
    the specific company, includes a call to action, and ends 
    professionally

    Return ONLY a JSON object in exactly this format, no extra text:
    "candidate_name": "name extracted from resume",
    "job_title": "role extracted from job description",
    "cover_letter": "full cover letter text here as a single 
    string with paragraph breaks using \n\n"
    '''
    )
    cleaned_text = cleanJSON(response.text)
    return cleaned_text