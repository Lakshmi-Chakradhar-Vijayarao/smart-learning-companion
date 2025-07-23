# ✅ summarizer.py (Hugging Face only)
from transformers import pipeline

# Force CPU for HF summarizer (MPS/Metal issues with BART models)
hf_summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    device=-1
)

# ──────────────── Utility: Word-aware chunking ────────────────
def chunk_text(text, max_chunk_words=450):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(current_chunk) + 1 <= max_chunk_words:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# ──────────────── Summarizer Function ────────────────
def summarize_text(text: str) -> str:
    if len(text.strip()) < 300:
        return "⚠️ Input too short to summarize meaningfully."

    chunks = chunk_text(text)
    results = []
    for chunk in chunks:
        if len(chunk.split()) < 40:
            continue
        result = hf_summarizer(chunk, max_length=130, min_length=40, do_sample=False)
        results.append(result[0]["summary_text"].strip())

    return " ".join(results).strip() or "⚠️ Text too short for summarization."
