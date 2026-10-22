import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL = os.getenv("MODEL", "gemini-3.5-flash-lite")
MAX_TOKENS = 4000
MIN_INTERVAL = float(os.getenv("MIN_INTERVAL", "4"))  # seconds between API calls