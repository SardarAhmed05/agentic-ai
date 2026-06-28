import json
import requests
from dotenv import load_dotenv
import os

def get_weather(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            lat = data['results'][0]['latitude']
            lon = data['results'][0]['longitude']

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['current_weather']['temperature']
    return f"Weather data for {city}: {str(data['current_weather'])}"
    
load_dotenv(dotenv_path="../.env")
api_key = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

tools = [
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city"
                }
            },
            "required": ["city"]
        }
    }
}
]

messages = [{"role": "system", "content": "You are a helpful weather assistant."}]

def agent():
    response = requests.post(url, headers=headers, json={
        "model": "openai/gpt-oss-20b",
        "messages": messages,
        "tools": tools,
        "temperature": 0.7
    })


    data = response.json()
    message = data["choices"][0]["message"]

    if message.get("tool_calls"):
        for tool_call in message["tool_calls"]:
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])

            # call the actual function
            result = get_weather(arguments["city"])

            messages.append(message)  # add the LLM's tool call request to history

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })

        final_response = requests.post(url, headers=headers, json={
            "model": "openai/gpt-oss-20b",
            "messages": messages,
            "tools": tools,
            "temperature": 0.7
        })

        final_answer = final_response.json()["choices"][0]["message"]["content"]

        return final_response.json()["choices"][0]["message"]["content"]

    else:
        return message["content"]
    
print("Welcome to the Weather Agent!")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break
    messages.append({"role": "user", "content": user_input})
    print("Agent:", agent())