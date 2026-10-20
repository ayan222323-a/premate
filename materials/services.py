from core.ai_client import ask_claude


def generate_notes(topic):
    system = 'You are a helpful tutor for college students preparing for campus placements in India.'
    prompt = f"""Write short revision notes on "{topic}" for a fresher preparing for placements.

Format rules (plain text only, no markdown symbols like ** or #):
- Start with a 2-3 line simple explanation.
- Then a section "Key points:" with 5 to 7 lines, each starting with "- ".
- Then a section "Common interview questions:" with 3 questions, each starting with "- ".
- Then a section "Quick example:" with one small example (code if relevant).
Keep the total under 300 words."""
    text = ask_claude(prompt, system=system, max_tokens=2048).strip()
    if not text:
        raise ValueError('AI se notes nahi mile, dobara try karo.')
    return text