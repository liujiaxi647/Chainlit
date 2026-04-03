import chainlit as cl
from google import genai
from google.genai import types
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a health behavior support assistant.
Keep responses concise, under 150 words.
Do not provide medical diagnoses or clinical advice.
Focus only on healthy eating or alcohol use topics."""

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    cl.user_session.set("turn_count", 0)

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("history", [])
    turn_count = cl.user_session.get("turn_count", 0)

    if turn_count >= 6:
        await cl.Message(
            content="Thank you! Please click the link to continue.\n\n"
                    "[Continue to Survey](https://your-qualtrics-url.com)"
        ).send()
        return

    history.append({"role": "user", "parts": [{"text": message.content}]})

    msg = cl.Message(content="")
    await msg.send()

    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=300,
        )
    )

    for chunk in response:
        if chunk.text:
            await msg.stream_token(chunk.text)

    await msg.update()

    history.append({"role": "model", "parts": [{"text": msg.content}]})
    cl.user_session.set("history", history)
    cl.user_session.set("turn_count", turn_count + 1)