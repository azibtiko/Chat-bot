import asyncio
from llm_support import generate_chatbot_response, classify_conversation

async def test_flow():
    user_msg = "I was charged twice this month and I want my money back."

    bot_reply = await generate_chatbot_response(user_msg)
    print("Bot reply:", bot_reply)

    category = await classify_conversation(user_msg, bot_reply)
    print("Detected category:", category)

if __name__ == "__main__":
    asyncio.run(test_flow())