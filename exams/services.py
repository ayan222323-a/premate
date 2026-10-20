import json
from core.ai_client import ask_claude


def generate_mcqs(subject, difficulty, count=5):
    system = 'You are an expert question-setter for campus placement exams in India.'
    prompt = f"""Create {count} multiple choice questions on "{subject}" at {difficulty} level
for a college student preparing for campus placements.

Reply ONLY with a JSON array. Each item must look like:
{{"question": "...", "options": ["text1", "text2", "text3", "text4"], "answer_index": 0, "explanation": "1-2 short sentences", "subtopic": "short topic name"}}

Rules: exactly 4 options, exactly one correct, answer_index is 0 to 3,
do not write A) B) C) D) inside options."""

    raw = ask_claude(prompt, system=system, max_tokens=4096, json_mode=True)
    raw = raw.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    data = json.loads(raw)

    mcqs = []
    for item in data:
        try:
            options = [str(o) for o in item['options']]
            idx = int(item['answer_index'])
            if len(options) == 4 and 0 <= idx < 4:
                mcqs.append({
                    'question': str(item['question']),
                    'options': options,
                    'answer_index': idx,
                    'explanation': str(item.get('explanation', '')),
                    'subtopic': str(item.get('subtopic', ''))[:100],
                })
        except (KeyError, TypeError, ValueError):
            continue

    if not mcqs:
        raise ValueError('AI se valid questions nahi mile, dobara try karo.')
    return mcqs[:count]