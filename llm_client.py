import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("⚠️ Error: GEMINI_API_KEY not found in .env")

# 2. Configure the Library
genai.configure(api_key=API_KEY)

# 3. Model Configuration
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 1024,
}

system_instruction = "You are a helpful AI assistant. Always communicate strictly in Afaan Oromoo."

def query_llm(user_input, history_input=[]):
    if not user_input.strip():
        return "Maaloo, gaaffii keessan barreessaa."

    try:
        # --- MODEL SELECTION ---
        # We try the fast model first. 
        # If your library is old, this name might fail, so we catch the error.
        model_name = "gemini-2.5-flash" 

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        # 4. Format History for Gemini
        gemini_history = []
        for msg in history_input:
            role = "user" if msg['role'] == "user" else "model"
            # Ensure parts is a list
            parts = msg['parts'] if isinstance(msg['parts'], list) else [msg['parts']]
            gemini_history.append({"role": role, "parts": parts})

        # 5. Start Chat
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_input)
        return response.text

    except Exception as e:
        error_msg = str(e)
        print(f"LLM Error: {error_msg}")
        
        # --- ERROR HANDLING ---
        if "404" in error_msg:
            return (
                "Rakkoo: Model 'gemini-2.5-flash' hin argamne. "
                "Furmaata: Terminal keessatti 'pip install --upgrade google-generativeai' jedhaa."
            )
        elif "400" in error_msg:
             return "Rakkoo: API Key ykn Request sirrii miti."
        else:
            return f"Rakkoo teeknikaa (VPN?): {error_msg}"