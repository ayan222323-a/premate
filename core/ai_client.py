import os
from google import genai
from google.genai import types

MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')


def ask_claude(prompt, system='', max_tokens=2048, json_mode=False):
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    config = types.GenerateContentConfig(
        system_instruction=system or None,
        max_output_tokens=max_tokens,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        response_mime_type='application/json' if json_mode else None,
    )
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config,
    )
    return response.text or ''