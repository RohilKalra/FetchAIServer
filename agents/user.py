from pydantic import BaseModel
from uagents import Agent, Context, Model
from asyncio import run
from uagents.context import send_sync_message
from models import *
from uagents.query import query


# This agent can ask a question to the AI model agent and display the answer.
# Note: Data returned by the AI model is not guaranteed to be correct. The purpose of this example is to show how to interact with such a model.

# Write your question here

gpt_address = "agent1qfvtufcgjwc6laspzpaz3gj00tph6e5gdq7pgqzw78frhwpnrgfv2tug7np"

user_mailbox_key = "e122baa3-94f7-4538-aa50-af3606c19788"
user = Agent(name="user", seed="s1", port="8003", mailbox=f"{user_mailbox_key}@https://agentverse.ai")

print("user address: ", user.address)

app_address = None

@user.on_message(model=Request)
async def ask_question(ctx: Context, sender: str, question: Request):
    ctx.logger.info(f"Asking question to AI model agent: {question.text}")
    global app_address
    app_address = sender
    # await ctx.send(gpt_address, question)

    try:
        response = await query(
        destination=gpt_address, message=question, timeout=15
        )
        print("response" + str(response))
        await ctx.send(sender, response)

    except Exception as e:
        print("error" + str(e))
        await ctx.send(sender, Data(value="unsuccessful agent call"))


@user.on_message(model=Data)
async def handle_data(ctx: Context, sender: str, data: Data):
    global app_address
    ctx.logger.info(app_address)
    ctx.logger.info(f"Got data from AI model agent: {data.value}")
    await ctx.send(app_address, Response(text=f"{data.value}"))

@user.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, error: Error):
    ctx.logger.info(f"Got error from AI model agent: {error}")

if __name__ == "__main__":
    user.run()