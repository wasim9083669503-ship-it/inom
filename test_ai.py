import google.generativeai as genai
import warnings
warnings.filterwarnings("ignore")

genai.configure(api_key="")
model = genai.GenerativeModel("gemini-2.5-flash-lite")

response = model.generate_content("Hello")
print(response.text)
