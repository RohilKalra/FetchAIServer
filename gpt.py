
# Here we demonstrate how an agent can respond to plain text questions with data from an AI model and convert it into a machine readable format.
# Note: the AI model used here is not actually able to verify its information and is not guaranteed to be correct. The purpose of this example is to show how to interact with such a model.
#
# In this example we will use:
# - 'agent': this is your instance of the 'Agent' class that we will give an 'on_interval' task
# - 'ctx': this is the agent's 'Context', which gives you access to all the agent's important functions
# - 'requests': this is a module that allows you to make HTTP requests
#
# To use this example, you will need to provide an API key for OPEN AI: https://platform.openai.com/account/api-keys
# You can define your OPENAI_API_KEY value in the .env file

import requests
import json
from uagents import Agent, Context, Model
from asyncio import run
import aiohttp
from models import *

gpt_mailbox_key = "916d4e9a-d139-4312-9a93-0f2e60a79e7f"
#gpt = Agent(name="gpt", seed="s2", port="8004", mailbox=f"{gpt_mailbox_key}@https://agentverse.ai")
gpt = Agent(name="gpt", seed="s2", port=8001, endpoint=["http://127.0.0.1:8001/submit"])

print("gpt address: ", gpt.address)

OPENAI_API_KEY = ""

if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
    raise Exception("You need to provide an API key for OPEN AI to use this example")

# Configuration for making requests to OPEN AI 
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MODEL_ENGINE = "gpt-3.5-turbo"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

# Send a prompt and context to the AI model and return the content of the completion
async def get_completion(context: str, prompt: str, max_tokens: int = 1024):
    data = {
        "model": MODEL_ENGINE,
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENAI_URL, headers=HEADERS, json=data) as response:
                response_data = await response.json()
                messages = response_data['choices']
                message = messages[0]['message']['content']
    except Exception as ex:
        print("An error occurred retrieving data from the AI model: " + str(ex))
        return None

    print("Got response from AI model: " + message)
    return message


# Instruct the AI model to retrieve data and context for the data and return it in machine readable JSON format
async def get_data(ctx: Context, request: str):
    context = '''    
    You are a helpful agent who can provide answers to questions along with sources and relevant context in a machine readable format.
    
    Please follow these guidelines:
    1. Try to answer the question as accurately as possible, using only reliable sources.
    2. Rate your confidence in the accuracy of your answer from 0 to 1 based on the credibility of the data publisher and how much it might have changed since the publishing date.
    3. Provide the information in the exact JSON format: {"value": value, "unit": unit, "timestamp": time, "confidence": rating, "source": ref, "notes": summary}
        - value is the string value of the data without any commas or units
        - unit is the measurement unit of the data if applicable, or an empty string if not applicable
        - time is the approximate timestamp when this value was published in ISO 8601 format
        - rating is your confidence rating of the data from 0 to 1
        - ref is a url where the data can be found, or a citation if no url is available
        - summary is a brief justification for the confidence rating (why you are confident or not confident in the accuracy of the value)
    
    Make sure to put the answer to the question in the "value" field of the JSON
    '''

    response = await get_completion(context, request, max_tokens=2048)
    #print(response)

    try:
        data = json.loads(response.splitlines()[-1])
        print(data)
        msg = Data.parse_obj(data)
        #print(msg)
        return msg
    except Exception as ex:
        ctx.logger.exception(f"An error occurred retrieving data from the AI model: {ex}")
        return Error(text="Sorry, I wasn't able to answer your request this time. Feel free to try again.")

# Message handler for data requests sent to this agent
@gpt.on_message(model=Request)
async def handle_request(ctx: Context, sender: str, request: Request):
    ctx.logger.info(f"Got request from {sender}: {request.text}")
    response = await get_data(ctx, request.text)
    await ctx.send(sender, response)

if __name__ == "__main__":
    gpt.run()