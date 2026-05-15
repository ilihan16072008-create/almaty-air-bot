import requests

IQAIR_API_KEY = "f99a1c7f-2992-404f-8e85-0c54d8aa3de9"

url = f"http://api.airvisual.com/v2/cities?state=Almaty Oblysy&country=Kazakhstan&key={IQAIR_API_KEY}"

response = requests.get(url)
print(response.json())