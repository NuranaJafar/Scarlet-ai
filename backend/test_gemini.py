import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY')

print(f"Testing Key: '{api_key}'")
print(f"Length: {len(api_key) if api_key else 0}")

if not api_key:
    print("Error: No GEMINI_API_KEY found in environment.")
    exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Hi")
    print("Success! Gemini response:")
    print(response.text)
except Exception as e:
    print(f"Failed! Error: {e}")
