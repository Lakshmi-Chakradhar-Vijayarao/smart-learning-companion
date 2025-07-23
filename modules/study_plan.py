# ✅ study_plan.py
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load local .env only if not running in Streamlit Cloud
if not st.secrets:
    load_dotenv()

# Use Streamlit secrets if available, else fallback to os.getenv
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_study_plan(topic: str, hours_per_day=2, goal="exam") -> str:
    prompt = f"""
    You are an expert AI academic assistant.
    Create a **realistic, technically focused 7-day study plan** for the topic: "{topic}".
    The learner can dedicate {hours_per_day} hours per day.
    The goal is to prepare for: {goal}.

    - Break it into specific subtopics based on common industry or academic structure.
    - Emphasize practical work (e.g., coding, problem sets, building prototypes).
    - Include self-evaluation like mock tests or concept checks.
    - Use technical terminology relevant to the topic.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=850,
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Failed to generate study plan: {str(e)}"
