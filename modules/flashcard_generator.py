
# ✅ flashcard_generator.py
import csv
from transformers import pipeline

nlp = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", aggregation_strategy="simple")

def generate_flashcards(text: str) -> list:
    entities = nlp(text)
    flashcards = []
    for ent in entities:
        term = ent['word']
        definition = f"Explain the term: {term}"
        flashcards.append({"term": term, "definition": definition})
    return flashcards

def export_flashcards_to_csv(flashcards: list, filename="flashcards.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Term", "Definition"])
        for card in flashcards:
            writer.writerow([card["term"], card["definition"]])
    return filename

