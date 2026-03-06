import os
from dotenv import load_dotenv

load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("KREA_API_KEY")

# Optional: check it
if api_key is None:
    print("KREA_API_KEY not set!")
else:
    print("KREA API key loaded successfully")
    print(api_key)