import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_PRO'))
model = genai.GenerativeModel('gemini-pro')

def generate_content(city):
    content = model.generate_content('Give 10 Places to Visit in '+ city +' in given json format {places:[{"placeName":  PLACE_NAME, "description":  DETAILED_DESCRIPTION_WITH_AT_LEAST_30_WORDS, "address": FULL_ADDRESS_OF_THE_PLACE}]}', generation_config=genai.types.GenerationConfig(max_output_tokens=2048))
    content.resolve()
    data = content.text[content.text.find('{'):]
    data = data[:data.rfind('}') + 1]
    data = json.loads(data)
    return data