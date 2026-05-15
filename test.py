import requests
from dotenv import load_dotenv
import os

load_dotenv()
IQAIR_API_KEY = os.getenv("IQAIR_API_KEY")

url = f"http://api.airvisual.com/v2/cities?state=Almaty Oblysy&country=Kazakhstan&key={IQAIR_API_KEY}"

response = requests.get(url)
print(response.json())
