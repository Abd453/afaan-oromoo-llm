import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

if not api_key:
    print("Error: API Key not found in .env")
else:
    genai.configure(api_key=api_key)
    
    print("--- Searching for available models ---")
    try:
        available_models = []
        for m in genai.list_models():
            # We are looking for models that support 'generateContent'
            if 'generateContent' in m.supported_generation_methods:
                print(f"Found: {m.name}")
                available_models.append(m.name)
        
        if not available_models:
            print("\nCRITICAL ERROR: No chat models found for this API key.")
        else:
            print(f"\n--- RECOMMENDED FIX ---")
            print(f"Open llm_client.py and change MODEL_NAME to:")
            # Usually the first one is the best bet, usually 'models/gemini-pro'
            print(f'MODEL_NAME = "{available_models[0]}"') 
            
            # Let's try to verify the first one works
            print(f"\nTesting {available_models[0]}...")
            model = genai.GenerativeModel(available_models[0])
            response = model.generate_content("Hello")
            print("Success! The model is working.")

    except Exception as e:
        print(f"Error checking models: {e}")