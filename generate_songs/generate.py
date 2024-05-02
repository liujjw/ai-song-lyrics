from openai import OpenAI
client = OpenAI()

MODEL_NAME = 'ft:gpt-3.5-turbo-1106:personal::95gmnd6a'

completion = client.chat.completions.create(
  model=MODEL_NAME,
  messages=[
    {"role": "system", "content": "You are a songwriter."},
    {"role": "user", "content": "Hello!"}
  ]
)
print(completion.choices[0].message)