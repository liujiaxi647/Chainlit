import chainlit as cl
import google.generativeai as genai

genai.configure(api_key="你的Gemini API Key")

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

    # 检查是否达到最大轮数
    if turn_count >= 6:
        await cl.Message(
            content="Thank you for the conversation! "
                    "Please click the link below to continue the survey.\n\n"
                    "[Continue to Survey](https://your-qualtrics-url.com)"
        ).send()
        return

    # 添加用户消息到历史
    history.append({
        "role": "user",
        "parts": [message.content]
    })

    # 创建模型
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        system_instruction=SYSTEM_PROMPT
    )

    # Streaming 回复
    msg = cl.Message(content="")
    await msg.send()

    response = model.generate_content(history, stream=True)
    for chunk in response:
        if chunk.text:
            await msg.stream_token(chunk.text)

    await msg.update()

    # 更新历史和轮数
    history.append({
        "role": "model",
        "parts": [msg.content]
    })
    cl.user_session.set("history", history)
    cl.user_session.set("turn_count", turn_count + 1)