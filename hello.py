#STEP 2 : Here we are giving a basic prompt to gemini through api and gettin an response
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads the .env file

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

response = client.chat.completions.create(
    model="gemini-3.5-flash-lite",
    messages=[{"role": "user", "content": "Explain what an API is in one sentence."}],
)

print(response.choices[0].message.content)
print(response.usage)

"""prompt_tokens=10: your question cost 10 tokens going in.
completion_tokens=29: the AI’s answer cost 29 tokens coming out.
total_tokens=39: the sum. Free tiers limit usage by tokens and requests, so later we’ll display this in the app."""