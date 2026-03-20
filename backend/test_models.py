import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY')

print(f"Testing Key: '{api_key}'")

if not api_key:
    print("Error: No GEMINI_API_KEY found in environment.")
    exit(1)

try:
    genai.configure(api_key=api_key)
    print("Available Models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Failed! Error: {e}")
