import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("KREA_API_KEY")

# Optional: check it
if api_key is None:
    print("KREA_API_KEY not set!")
else:
    print("KREA API key loaded successfully")
    print(api_key)

def sendRequest():
    # url = "https://api.krea.ai/jobs?limit=100&status=queued"
    url = "https://api.krea.ai/jobs?limit=100"
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(url, headers=headers)
    print("PRINTING response.text from sendrequest!!!")
    json_obj = response.json()
    print(json_obj["items"])
    # print(response.text)

sendRequest()