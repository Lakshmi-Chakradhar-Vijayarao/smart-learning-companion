# ✅ flashcard_generator.py
import csv
import os
import streamlit as st
from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

# Secure Hugging Face token from Streamlit secrets or fallback to env
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))

# Load NER model with token
nlp = pipeline(
    "ner",
    model="dbmdz/bert-large-cased-finetuned-conll03-english",
    aggregation_strategy="simple",
    token=HF_TOKEN
)

# ───────────────────────────── Flashcard Generator ─────────────────────────────
def generate_flashcards(text: str) -> list:
    entities = nlp(text)
    flashcards = []
    for ent in entities:
        term = ent['word']
        definition = f"Explain the term: {term}"
        flashcards.append({"term": term, "definition": definition})
    return flashcards

# ───────────────────────────── CSV Exporter ─────────────────────────────
def export_flashcards_to_csv(flashcards: list, filename="flashcards.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Definition"])
        for card in flashcards:
            writer.writerow([card["term"], card["definition"]])
    return filename
