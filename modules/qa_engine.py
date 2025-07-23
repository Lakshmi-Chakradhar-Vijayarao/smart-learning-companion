# ✅ qa_engine.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_question(text: str, question: str) -> str:
    prompt = f"""
    Given the following content, answer the user's question clearly and concisely.

    Content:
    {text}

    Question: {question}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ QA failed: {str(e)}"
