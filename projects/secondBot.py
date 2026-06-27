# Weather CHATBOT with async.

from dotenv import load_dotenv
import os
import requests
import json
import aiohttp
import asyncio

load_dotenv(dotenv_path="../.env")
api_key = os.getenv("GROQ_API_KEY")

async def get_coordinates(session, city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}
    
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            if "results" not in data or len(data["results"]) == 0:
                print(f"No results found for {city_name}")
                return None, None
            result = data["results"][0]
            return result['latitude'], result['longitude']
        else:
            print(f"Failed to get coordinates for {city_name}")
            return None, None
    
async def get_weather(session, city_lat, city_lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": city_lat,
        "longitude": city_lon,
        "current_weather": "true"
    }

    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            weather = data["current_weather"]
            return weather

        else:
            print(f"Failed to get weather data: Error {response.status}")

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

async def chat(messages, session, user_input):
    messages.append({"role": "user", "content": user_input})

    body = {
        "model": "openai/gpt-oss-20b",
        "messages": messages,
        "temperature": 0.7
    }

    async with session.post(url, headers=headers, json=body) as response:
        data = await response.json()
        reply = data["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": reply})
        if response.status != 200:
            return "Sorry, I couldn't get a response. Try again."
        return reply


async def main():
    async with aiohttp.ClientSession() as session:
        print("Welcome to the Weather CHATBOT!")
        city_name = (input("Enter a city name to get its weather: "))
        messages = [{"role": "system", "content": f"You are a weather assistant for {city_name}. You provide weather information based on the user's input."}]

        city_lat, city_lon = await get_coordinates(session, city_name)
        if city_lat is None or city_lon is None:
            print("Could not find city. Exiting.")
            exit()

        weather = await get_weather(session, city_lat, city_lon)
        if weather:
            print(f"Current weather in {city_name}:")
            print(f"Temperature: {weather['temperature']}°C")
            print("\n")
            first_message = f"The current weather in {city_name} is {weather['temperature']}°C, windspeed {weather['windspeed']} km/h, wind direction {weather['winddirection']}°. Describe this weather conversationally."
            print("Weather Assistant: ", await chat(messages, session, first_message))

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting the Weather CHATBOT. Goodbye!")
                break
            response = await chat(messages, session, user_input)
            print(f"Weather Assistant: {response}")

asyncio.run(main())