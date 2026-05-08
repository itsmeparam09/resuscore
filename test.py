import API_calls
import parser
api_key = API_calls.api_key
resume = "Param Khurana Resume New Final.pdf"
cover_letter = "Cover letter final.pdf"
job_description = '''What You'll Be Doing
Build, deploy, and maintain AI agents and workflows that own real parts of the partnerships function, including reporting, support, performance analytics, partner outreach, content, enablement, and market intelligence.
Ship production reporting in Metabase that we send directly to external partners, and iterating on the dashboards based on partner feedback.
Identify anomalies, funnel breakages, and data quality issues by building agents that monitor and flag them proactively.
Draft partner-facing content (one-pagers, campaign briefs, outreach sequences, enablement material) using AI as a co-author and Relay's voice as the source of truth.
Sit in on partner calls, strategy sessions, and internal reviews, and turn the messy outputs into structured artifacts the team can act on.
Document everything you build so the next person, human or agent, can pick it up and run.
Who You Are
You're AI-native. Claude, ChatGPT, and / or other AI tools are languages that your building and learning from every day. You can describe an agent you've built, a workflow you've automated, or a problem you've solved that a year ago you could not have.
You’re an AI-builder, not just an AI-user. Vibe-coded side projects, scrappy internal tools, scripts that saved you hours. We don't care about the form, we care that you experiment!
You’re comfortable with data; reasoning about funnels, conversion rates, and unit economics.
You're curious about business. You want to understand why partnerships matter, how SMB fintech works, and what makes a good partner relationship, not just execute on tickets.
You're proactive and self-sufficient: you can take a vague problem, ask the right probing questions, and come back with a working v1.
You bring a learner's mindset. You'll be operating at the edge of what's possible with current AI tooling, which means a lot of "I don't know yet, let me figure it out".
'''

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
    letter = API_calls.GenereateLetter(api_key, job_description, resume_string)
    return letter
