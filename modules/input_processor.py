# modules/input_processor.py
"""
Unified ingestion module
----------------------------------
• YouTube -> transcript (or Whisper fallback)
• Audio   -> Whisper transcription
• PDF/DOCX/TXT -> raw text (your code reused)
"""

import tempfile, os
from typing import Optional
import yt_dlp, whisper, fitz               # PyMuPDF
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from docx import Document

# Whisper model cached once
_whisper = whisper.load_model("base")      # base is fine on M2; tiny is faster

# ----------  YOUR RESUME/PDF/TXT/DOCX EXTRACTOR  ----------
def _extract_text_from_file(uploaded_file) -> Optional[str]:
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == "txt":
        return uploaded_file.read().decode("utf-8")

    if file_type == "docx":
        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)

    if file_type == "pdf":
        text = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    return None
# ----------------------------------------------------------

def _transcribe(path: str) -> str:
    return _whisper.transcribe(path)["text"]

def _download_audio(url: str, out_dir: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.join(out_dir, f"{info['id']}.{info['ext']}")

def _yt_transcript(url: str) -> Optional[str]:
    try:
        vid = url.split("watch?v=")[-1].split("&")[0]
        data = YouTubeTranscriptApi.get_transcript(vid, languages=["en"])
        return " ".join(d["text"] for d in data)
    except TranscriptsDisabled:
        return None

# -----------  PUBLIC ENTRY POINT  -------------------------
def handle_input(youtube_url: str = "",
                 uploaded_file=None,
                 raw_text: str = "") -> str:
    """Return plain text ready for downstream modules."""
    # 1) YouTube pipeline
    if youtube_url:
        txt = _yt_transcript(youtube_url)
        if txt:
            return txt            # transcript exists
        # fallback: DL audio + Whisper
        with tempfile.TemporaryDirectory() as tmp:
            audio_fp = _download_audio(youtube_url, tmp)
            return _transcribe(audio_fp)

    # 2) File upload pipeline
    if uploaded_file is not None:
        txt = _extract_text_from_file(uploaded_file)
        if txt:
            return txt
        # If it’s an audio file
        if uploaded_file.name.split('.')[-1].lower() in ("mp3", "wav"):
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp.flush()
                return _transcribe(tmp.name)

    # 3) Raw text
    if raw_text.strip():
        return raw_text

    return ""
# -----------  TEXT SPLITTER (for embedding) -----------------
def split_text_into_chunks(text: str, max_chunk_length: int = 200) -> list[str]:
    """
    Splits long text into smaller chunks for vector embedding.

    Args:
        text (str): The input text to be split.
        max_chunk_length (int): Max number of characters per chunk.

    Returns:
        list[str]: A list of text chunks.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk + [word])) <= max_chunk_length:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

