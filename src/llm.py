import time
from openai import OpenAI, RateLimitError, APIConnectionError, InternalServerError
from src.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS, MIN_INTERVAL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, max_retries=0)  # we do our own retries

RETRYABLE = (RateLimitError, APIConnectionError, InternalServerError)
_last_call = 0.0


def _throttle():
    """Free tiers allow only N requests/minute, so space calls out on purpose."""
    global _last_call
    wait = MIN_INTERVAL - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


def _with_system(messages, system):
    return ([{"role": "system", "content": system}] if system else []) + messages


def call(messages, system="", max_tokens=MAX_TOKENS, max_retries=5):
    """One request. Returns (text, usage). Retries with exponential backoff."""
    for attempt in range(max_retries):
        try:
            _throttle()
            response = client.chat.completions.create(
                model=MODEL, messages=_with_system(messages, system), max_tokens=max_tokens
            )
            return response.choices[0].message.content, response.usage
        except RETRYABLE as e:
            if attempt == max_retries - 1:
                raise
            delay = 2 ** attempt * 3  # 3s, 6s, 12s, 24s
            print(f"[retry {attempt + 1}] {type(e).__name__}, waiting {delay}s")
            time.sleep(delay)


def stream(messages, system="", max_tokens=MAX_TOKENS):
    """Yields the reply in small pieces as they arrive."""
    _throttle()
    response = client.chat.completions.create(
        model=MODEL, messages=_with_system(messages, system),
        max_tokens=max_tokens, stream=True,
    )
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content