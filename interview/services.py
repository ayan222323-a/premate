import json
import pdfplumber
from core.ai_client import ask_claude


def extract_text_from_pdf(file_path):
    text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or '') + '\n'
    return text.strip()


def generate_questions(resume_text, job_role, count=5):
    system = 'You are an experienced interviewer for campus placements in India.'
    prompt = f"""Candidate resume:
{resume_text[:6000]}

Target role: {job_role}

Generate {count} interview questions based on this resume: a mix of HR and technical,
suited for a fresher. Reply ONLY with a JSON array of strings, no extra text.
Example: ["Question 1?", "Question 2?"]"""

    raw = ask_claude(prompt, system=system, max_tokens=2048, json_mode=True)
    raw = raw.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    questions = json.loads(raw)
    return [q for q in questions if isinstance(q, str)][:count]


def evaluate_answer(question, answer, job_role):
    system = 'You are a strict but encouraging interviewer for campus placements in India.'
    prompt = f"""Role: {job_role}
Question: {question}
Candidate's answer: {answer}

Evaluate the answer. Reply ONLY with a JSON object, no extra text:
{{"score": <number from 0 to 10>, "feedback": "<2-3 short sentences: what was good, what to improve>"}}"""

    raw = ask_claude(prompt, system=system, max_tokens=1024, json_mode=True)
    raw = raw.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    try:
        data = json.loads(raw)
        score = float(data.get('score', 0))
        feedback = str(data.get('feedback', ''))
    except (json.JSONDecodeError, ValueError, TypeError):
        return 0.0, 'Feedback generate nahi ho paya. Dobara try karo.'
    return max(0.0, min(10.0, score)), feedback