import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY not found in .env")

# Configure the SDK
genai.configure(api_key=API_KEY)

# Use the correct stable model name
# (There is no 2.5 yet, 1.5 Flash is the latest fast version)
MODEL_NAME = "gemini-1.5-flash"

def query_llm(user_input):
    """
    Sends user input to Google Gemini (requires VPN in Ethiopia).
    """
    if not user_input.strip():
        return "Please enter a question."

    try:
        # Initialize model
        model = genai.GenerativeModel(MODEL_NAME)

        # Create the prompt to enforce Afaan Oromoo
        prompt = f"You are a helpful AI assistant. Answer the following question strictly in Afaan Oromoo: {user_input}"

        # Generate content
        response = model.generate_content(prompt)

        # Return text
        return response.text

    except Exception as e:
        return f"Gemini Error: {e} (Did you turn on your VPN?)"