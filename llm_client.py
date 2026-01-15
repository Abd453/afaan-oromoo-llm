import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the new Client
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash" # Use the stable string

def query_llm(user_input, history_input=[]):
    if not user_input.strip():
        return "Maaloo, gaaffii keessan barreessaa."

    # Convert your history format to the new SDK format if needed
    # (The new SDK uses a slightly different structure)
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful AI assistant. Always communicate strictly in Afaan Oromoo.",
                temperature=0.7,
            ),
        )

        return response.text

    except Exception as e:
        return f"Gorsa: VPN keessan banameeraa? Dogoggora: {e}"