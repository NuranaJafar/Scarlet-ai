from openai import OpenAI
import os

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def generate_response(self, messages, model='gpt-4o-mini', temperature=0.85):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=500
        )
        return response.choices[0].message.content

