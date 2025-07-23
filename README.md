# 🎓 Smart Learning Companion 2.0

Your personalized study assistant powered by **Transformers**, **Whisper**, and **Streamlit** — all running locally with modular Python components.

---

## 🚀 Demo

🌐 **Live App**: [Click to launch](https://lakshmi-chakradhar-vijayarao-smart-learning-companion.streamlit.app)  
📽️ **Demo Video**: [Watch Demo](#) *(Replace with actual video link)*

---

## 🧠 What It Does

**Smart Learning Companion 2.0** allows you to upload or paste learning content from various sources and get a full-fledged personalized study toolkit:

### ✨ Supported Inputs:
- 📄 PDF documents
- 🔗 YouTube videos (via transcript)
- 🎧 Audio files (MP3/WAV)
- ✍️ Raw text

### 🛠️ Features:
| Feature | Description |
|--------|-------------|
| 📜 **Transcript Generator** | Extracts transcripts from YouTube/audio using **Whisper** |
| ✂️ **Concise Summarization** | Uses `distilbart-cnn` to summarize key points locally |
| ❓ **Interactive Q&A** | Ask questions and get answers using `distilbert-squad` |
| 📘 **Vocabulary Builder** | Extracts technical terms + simple explanations |
| 📝 **Quiz Generator** | Auto-generates MCQs and fill-in-the-blank questions |
| 🎴 **Flashcards** | Download key terms/Q&A as CSV flashcards |
| 📆 **Study Plan Generator** | Suggests daily/weekly plans based on your time commitment |
| 🔍 **Related Resources** | Suggests related YouTube videos, Wikipedia articles |
| 📥 **Export Options** | Download everything as `.docx` with full formatting |

---

## 🧩 Tech Stack

- 🧠 **Transformers** (Summarization, Q&A, Fill-in-the-blank)
- 🔊 **Whisper** (Speech-to-text)
- 🌐 **Streamlit** (Frontend + session memory)
- 📦 **Modular Python Backend** (Custom logic for each feature)
- 📄 **DOCX Export** (via `python-docx`)
- 📃 **PDF Export** (via `WeasyPrint`)
- 🔐 **OpenAI API** (Used only for vocab extraction)

---

## 💻 Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/Lakshmi-Chakradhar-Vijayarao/smart-learning-companion.git
cd smart-learning-companion

# 2. Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key in a `.env` file
echo 'OPENAI_API_KEY=your-api-key-here' > .env

# 5. Run the app
streamlit run app.py
