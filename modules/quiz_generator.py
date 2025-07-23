# ✅ quiz_generator.py
#import os
#from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



import os
import streamlit as st
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key)



# ─────────── 1. Bulk Quiz Generator ─────────────────────────
def generate_quiz(text: str, num_questions: int = 5) -> list:
    prompt = f"""
    Generate {num_questions} multiple choice questions from the following text.
    Each question should include 4 options and identify the correct answer.

    Format as a Python list of dictionaries like this:
    [
      {{
        "question": "What is ...?",
        "options": ["A", "B", "C", "D"],
        "answer": "B"
      }},
      ...
    ]

    Text:
    \"\"\"{text}\"\"\"
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.5,
        )
        result = response.choices[0].message.content.strip()
        return eval(result) if result.startswith("[") else []
    except Exception as e:
        return [f"❌ Quiz generation failed: {str(e)}"]

# ─────────── 2. Per-Term MCQ Generator ──────────────────────
def generate_mcq(term: str, definition: str) -> dict:
    prompt = f"""
    Create a multiple-choice question for the term "{term}".
    Use the definition: "{definition}"
    Include 4 options, and indicate the correct answer.

    Format as:
    {{
        "question": "...?",
        "options": ["A", "B", "C", "D"],
        "answer": "Correct Option"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.4,
        )
        return eval(response.choices[0].message.content.strip())
    except Exception as e:
        return {
            "question": f"❌ Failed to generate MCQ for '{term}'",
            "options": [],
            "answer": str(e)
        }

# ─────────── 3. Per-Term Fill-in-the-Blank Generator ───────
def generate_fill_blank(term: str, definition: str) -> dict:
    prompt = f"""
    Create a fill-in-the-blank question using the term "{term}" and its definition: "{definition}".
    Return the result as a Python dictionary with keys 'question' and 'answer'.
    Example:
    {{
        "question": "____ is used for ...",
        "answer": "{term}"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
        )
        return eval(response.choices[0].message.content.strip())
    except Exception as e:
        return {
            "question": f"❌ Failed to generate fill-in-the-blank for '{term}'",
            "answer": str(e)
        }
