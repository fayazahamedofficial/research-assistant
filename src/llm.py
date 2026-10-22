from openai import OpenAI
from src.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def stream(messages, system="", max_tokens=MAX_TOKENS):
    """Yields the reply in small pieces as they arrive."""
    if system:
        messages = [{"role": "system", "content": system}] + messages

    response = client.chat.completions.create(
        model=MODEL, messages=messages, max_tokens=max_tokens, stream=True
    )
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content