# Weather CHATBOT
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

def get_coordinates(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "results" not in data or len(data["results"]) == 0:
            print(f"No results found for {city_name}")
            return None, None
        result = data["results"][0]
        return result['latitude'], result['longitude']
    else:
        print(f"Failed to get coordinates for {city_name}")
        return None, None
    
def get_weather(city_lat, city_lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": city_lat,
        "longitude": city_lon,
        "current_weather": True
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        weather = data["current_weather"]
        return weather

    else:
        print(f"Failed to get weather data: {response.status_code}")

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

messages = [{"role": "system", "content": "You are a weather assistant. You provide weather information based on the user's input."}]

def chat(user_input):
    messages.append({"role": "user", "content": user_input})

    response = requests.post(url, headers=headers, json={
        "model": "openai/gpt-oss-20b",
        "messages": messages,
        "temperature": 0.7
    })

    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})
    if response.status_code != 200:
        return "Sorry, I couldn't get a response. Try again."
    return reply

print("Welcome to the Weather CHATBOT!")

city_name = (input("Enter a city name to get its weather: "))
city_lat, city_lon = get_coordinates(city_name)
if city_lat is None or city_lon is None:
    print("Could not find city. Exiting.")
    exit()

if city_lat is not None and city_lon is not None:
    weather = get_weather(city_lat, city_lon)
    if weather:
        print(f"Current weather in {city_name}:")
        print(f"Temperature: {weather['temperature']}°C")
        print("\n")
        first_message = f"The current weather in {city_name} is {weather['temperature']}°C, windspeed {weather['windspeed']} km/h, wind direction {weather['winddirection']}°. Describe this weather conversationally."
        print("Weather Assistant: ", chat(first_message))
    else:
        print("Could not retrieve weather data.")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the Weather CHATBOT. Goodbye!")
        break
    response = chat(user_input)
    print(f"Weather Assistant: {response}")