import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Configure with Env Var
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Available Gemini Models:")
try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
