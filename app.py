import os
import chainlit as cl
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

    history.append({"role": "user", "content": message.content})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    msg = cl.Message(content="")
    await msg.send()

    full_text = ""

    try:
        stream = client.chat.completions.create(
            model="gpt-5.4",
            messages=messages,
            temperature=0.7,
            max_completion_tokens=300,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_text += delta
                await msg.stream_token(delta)

        msg.content = full_text if full_text.strip() else "[No response returned]"
        await msg.update()

    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        return

    history.append({"role": "assistant", "content": full_text})
    cl.user_session.set("history", history)
    cl.user_session.set("turn_count", turn_count + 1)