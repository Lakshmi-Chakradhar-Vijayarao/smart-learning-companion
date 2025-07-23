# ✅ vocab_helper.py
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from transformers import pipeline

# Load environment variables only in local dev
if not st.secrets:
    load_dotenv()

# Get OpenAI API key from Streamlit secrets or fallback to env
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=OPENAI_API_KEY)

# HF pipeline for local explanation (no API call)
explain_pipe = pipeline("text2text-generation", model="google/flan-t5-base", device=-1)

# ─────────────────────────────────────────────────────
def extract_key_terms(text: str, top_k: int = 10) -> list:
    """
    Extracts the top technical terms or domain-specific keywords from the given text.
    Uses OpenAI to ensure high-quality, relevant terms. 
    Returns a Python list of terms (strings).
    """
    prompt = f"""
    From the following text, extract the {top_k} most relevant technical terms or domain-specific keywords.
    Ignore vague English words, slang, or general terms.
    Return only a valid Python list of strings. No explanations.

    Text:
    \"\"\"{text}\"\"\"
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.2,
        )
        terms = response.choices[0].message.content.strip()
        return eval(terms) if terms.startswith("[") else []
    except Exception as e:
        return [f"❌ Extraction failed: {str(e)}"]

# ─────────────────────────────────────────────────────
def get_vocab_explanation(term: str) -> str:
    """
    Provides a simple explanation for the given technical term using a local HuggingFace model.
    """
    prompt = f"Explain the term '{term}' in simple words suitable for a student."
    try:
        result = explain_pipe(prompt, max_length=64, do_sample=False)
        return result[0]["generated_text"].strip()
    except Exception as e:
        return f"❌ Explanation failed: {str(e)}"
