import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv('../.env.prod/.env')

def create_opneaiclient_async():
    return AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))