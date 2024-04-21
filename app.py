import asyncio
#from flask import Flask, request, jsonify
from uagents import Agent, Context, Model
from uagents.query import query
import json
from uagents.context import send_sync_message
from fastapi import FastAPI
from models import *
from fastapi.middleware.cors import CORSMiddleware
#from mangum import Mangum

# Create an agent
# appAgent = Agent(name="gpt", seed="sn")
# print("appAgent address: ", appAgent.address)


user_address = "agent1qff8q8ns2tsmvru2cdm0l3kpqcuvn7dv9r2hghwt0qsta3k60j2z7n07xde"
gpt_address = "agent1qfvtufcgjwc6laspzpaz3gj00tph6e5gdq7pgqzw78frhwpnrgfv2tug7np"

app = FastAPI()
#handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/hint")
async def hint(req: Request):
    req = Request(text=f'''Asking question to AI model agent: I'm playing a game\
    where I want to give vague hints to a user to help them guess a food. I will\
    ask you, ChatGPT, to generate the vague hints. Generate a vague hint for the food: {req.text}. DO NOT MAKE IT OBVIOUS WHAT THE FOOD IS. Limit to 8 words max.''')
    print("req" + str(req))
    try:
        response = await send_sync_message(
        gpt_address, req, response_type=Data)
        print("response" + str(response))
        return response

    except Exception as e:
        print("error" + str(e))
        return "unsuccessful agent call"

