import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Use Stable Model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

try:
    response = model.generate_content("Hello")
    print(f"Astra Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
