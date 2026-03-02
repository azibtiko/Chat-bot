import os
import time
from typing import Optional
from groq import AsyncGroq
from dotenv import load_dotenv

from .ai_prompts import CHATBOT_SYSTEM_PROMPT, CLASSIFICATION_PROMPT_TEMPLATE

load_dotenv()

groq_client = AsyncGroq(api_key=os.getenv("grok_api_key"))

DEFAULT_MODEL = "llama-3.3-70b-versatile"
FAST_MODEL = "llama-3.1-8b-instant"

async def generate_chatbot_response(
    user_message: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 450,
) -> str:
    messages = [
        {"role": "system", "content": CHATBOT_SYSTEM_PROMPT}
    ]

    messages.append({"role": "user", "content": user_message})

    try:
        start_time = time.time()
        response = await groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
        )
        end_time = time.time()
        response_time = int((end_time - start_time) * 1000)
        return response.choices[0].message.content.strip(), response_time
    except Exception:
        return "I'm sorry, I'm having trouble connecting right now. Please try again in a moment."

async def classify_conversation(
    user_message: str,
    bot_response: str,
    model: str = FAST_MODEL,
    temperature: float = 0.0,
) -> str:
    prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(
        user_message=user_message.strip(),
        bot_response=bot_response.strip()
    )

    try:
        response = await groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=30,
        )

        category = response.choices[0].message.content.strip()

        valid_categories = {
            "Billing", "Refund", "Account Access",
            "Cancellation", "General Inquiry"
        }

        for cat in valid_categories:
            if cat.lower() in category.lower():
                return cat

        return "General Inquiry"

    except Exception:
        return "General Inquiry"