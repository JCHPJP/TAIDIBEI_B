import openai
from dotenv import load_dotenv
import os
load_dotenv()

def getAgent(api_key:str, base_url:str):
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    return client


client = getAgent(os.getenv("PARATERA_API_KEY",), 
                   os.getenv("PARATERA_BASE_URL",))
response = client.chat.completions.create(
    model="DeepSeek-V3.2",  # model to send to the proxy
    messages=[
        {
            "role": "user",
            "content": "你是谁"        
        }
    ]
)
print(response)