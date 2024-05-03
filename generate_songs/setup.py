import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('../.env.prod/.env')

def create_opneaiclient():
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))