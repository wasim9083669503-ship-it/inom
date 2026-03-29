import google.generativeai as genai
import warnings
warnings.filterwarnings("ignore")

genai.configure(api_key="")

models = []
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        models.append(m.name)

# Print only gemini-2 flash models
for name in models:
    if "gemini-2" in name and "flash" in name:
        print(name)
