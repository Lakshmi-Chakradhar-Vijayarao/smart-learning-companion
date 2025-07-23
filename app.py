import streamlit as st
from dotenv import load_dotenv
import os, json, tempfile

from modules.input_processor import handle_input
from modules.summarizer import summarize_text
from modules.qa_engine import ask_question
from modules.vocab_helper import extract_key_terms, get_vocab_explanation
from modules.quiz_generator import generate_mcq, generate_fill_blank
from modules.flashcard_generator import export_flashcards_to_csv
from modules.study_plan import generate_study_plan
from modules.resource_recommender import search_wikipedia, get_google_scholar_resources, get_arxiv_papers
from modules.docx_exporter import export_docx

load_dotenv()

st.set_page_config("Smart Learning Companion 2.0", layout="wide")
st.title("📚 Smart Learning Companion\u00a02.0")

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

# ─────────── 1. INPUT  ─────────────────────────────────
st.header("① Provide Your Content")

with st.expander("Upload / Paste / Link", expanded=True):
    col1, col2 = st.columns(2)
    youtube_url = col1.text_input("YouTube URL")
    uploaded_file = col1.file_uploader("Upload PDF, DOCX, TXT, MP3/WAV", type=["pdf", "docx", "txt", "mp3", "wav"])
    raw_text = col2.text_area("Or paste text here")

    if st.button("🔍 Extract Text"):
        with st.spinner("Processing…"):
            st.session_state.doc_text = handle_input(
                youtube_url=youtube_url,
                uploaded_file=uploaded_file,
                raw_text=raw_text,
            )
        if st.session_state.doc_text:
            st.success("Text extracted ✓")
        else:
            st.error("No valid input detected.")

if st.session_state.doc_text:
    with st.expander("🔗 Raw Extract (first 10 000 chars)"):
        st.write(st.session_state.doc_text[:10000] + (" ..." if len(st.session_state.doc_text) > 10000 else ""))

# ─────────── 2. SUMMARIES  ───────────────────────
if st.session_state.doc_text:
    st.header("② Summaries")

    if st.button("🧠 Generate Summaries"):
        with st.spinner("Summarizing…"):
            summary = summarize_text(st.session_state.doc_text)
            st.session_state.concise = summary
        st.success("Summaries ready!")

    if "concise" in st.session_state:
        st.subheader("Concise Summary")
        st.markdown(st.session_state.concise)

# ─────────── 3. Q&A  ──────────────────────
if st.session_state.doc_text:
    st.header("③ Ask Questions")
    q = st.text_input("Your question")
    if st.button("❓ Answer"):
        if not q.strip():
            st.warning("Type a question first.")
        else:
            with st.spinner("Searching answer…"):
                ans = ask_question(st.session_state.doc_text, q)
            st.write(f"**Answer:** {ans}")
            if "qa_pairs" not in st.session_state:
                st.session_state.qa_pairs = []
            st.session_state.qa_pairs.append((q, ans))

# ─────────── 4. VOCAB  ─────────────────────
if "concise" in st.session_state:
    st.header("④ Vocabulary Helper")
    if st.button("📚 Extract Terms"):
        terms = extract_key_terms(st.session_state.concise, top_k=10)
        explanations = {t: get_vocab_explanation(t) for t in terms}
        st.session_state.vocab = explanations
        st.success("Vocabulary ready!")

    if "vocab" in st.session_state:
        for term, expl in st.session_state.vocab.items():
            st.markdown(f"**{term}** — {expl}")

        bad_terms = [t for t in st.session_state.vocab if len(t) <= 4 or t.lower() in ["lot", "thing", "goal", "trusty"]]
        if bad_terms:
            st.warning(f"⚠️ Some extracted terms may be too generic: {', '.join(bad_terms)}")

# ─────────── 5. QUIZ & FLASHCARDS  ─────────────────
if "vocab" in st.session_state:
    st.header("⑤ Quiz & Flashcards")

    if st.button("📝 Create Quiz"):
        mcqs = []
        blanks = []
        for term, definition in st.session_state.vocab.items():
            mcqs.append(generate_mcq(term, definition))
            blanks.append(generate_fill_blank(term, definition))

        st.session_state.mcqs = mcqs
        st.session_state.blanks = blanks
        st.success("Quiz generated!")

    if "mcqs" in st.session_state:
        for i, q in enumerate(st.session_state.mcqs, 1):
            st.markdown(f"**Q{i}. {q['question']}**")
            st.write(q["options"])
            with st.expander("Answer"):
                st.write(q["answer"])

        flashcards = [{"term": t, "definition": d} for t, d in st.session_state.vocab.items()]
        csv_path = export_flashcards_to_csv(flashcards)
        st.download_button(
            label="⬇️ Download Flashcards CSV",
            data=open(csv_path, "rb").read(),
            file_name="flashcards.csv",
            mime="text/csv"
        )

# ─────────── 6. STUDY PLAN  ─────────────────
if "vocab" in st.session_state:
    st.header("⑥ Personalized Study Plan")
    hours = st.slider("Hours per day", 1, 6, 2)
    goal = st.selectbox("Goal", ["exam", "project", "general understanding"])

    if st.button("🗓️ Generate Study Plan"):
        with st.spinner("AI is planning…"):
            terms = list(st.session_state.vocab.keys())
            plan = generate_study_plan(terms, hours, goal)
            st.session_state.plan = plan
        st.markdown(st.session_state.plan)

# ─────────── 7. RELATED RESOURCES  ─────────────
if "vocab" in st.session_state:
    st.header("⑦ Related Resources")
    query = st.text_input("Topic keyword for extra resources", value=list(st.session_state.vocab.keys())[0] if st.session_state.vocab else "")

    if st.button("🔗 Fetch Resources"):
        wiki_summary, wiki_link = search_wikipedia(query.strip())

        st.subheader("📘 Wikipedia Summary")
        if "failed" in wiki_summary.lower():
            st.warning("❌ Could not fetch Wikipedia summary.")
        else:
            st.write(wiki_summary)
            if wiki_link:
                st.markdown(f"[🔗 Read more on Wikipedia]({wiki_link})")

        st.subheader("📄 Recommended Papers")
        arxiv_results = get_arxiv_papers(query)
        scholar_results = get_google_scholar_resources(query)

        all_resources = arxiv_results + scholar_results
        st.session_state.related_resources = all_resources
        if all_resources:
            for paper in all_resources:
                st.markdown(
                    f"**[{paper['title']}]({paper['link']})**  \n"
                    f"*Source:* {paper.get('source', 'Unknown')}  \n\n"
                    f"{paper['summary']}"
                )
        else:
            st.warning("❌ No papers found.")

# ─────────── 8. EXPORT DOCX  ─────────────────
if st.session_state.doc_text:
    st.header("⑧ Export Full Report")
    if st.button("📄 Build Word Report (.docx)"):
        sections = []

        # ① Input Content Preview
        preview = st.session_state.doc_text[:1000]
        sections.append({
            "title": "① Input Content Preview",
            "content": preview + ("..." if len(st.session_state.doc_text) > 1000 else "")
        })

        # ② Concise Summary
        summary = st.session_state.get("concise", "No summary generated.")
        sections.append({
            "title": "② Concise Summary",
            "content": summary.strip()
        })

        # ③ Q&A Section
        qa_pairs = st.session_state.get("qa_pairs", [])
        if qa_pairs:
            qa_content = "\n\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(qa_pairs)])
        else:
            qa_content = "No questions asked."
        sections.append({
            "title": "③ Q&A Section",
            "content": qa_content
        })

        # ④ Vocabulary
        vocab = st.session_state.get("vocab", {})
        if vocab:
            vocab_content = "\n".join([f"{term}: {definition}" for term, definition in vocab.items()])
        else:
            vocab_content = "No terms extracted."
        sections.append({
            "title": "④ Vocabulary",
            "content": vocab_content
        })

        # ⑤ Quiz (MCQs)
        mcqs = st.session_state.get("mcqs", [])
        if mcqs:
            quiz_content = ""
            for i, q in enumerate(mcqs, 1):
                opts = "\n".join([f"  - {opt}" for opt in q['options']])
                quiz_content += f"Q{i}: {q['question']}\n{opts}\nAnswer: {q['answer']}\n\n"
        else:
            quiz_content = "No quiz generated."
        sections.append({
            "title": "⑤ Quiz",
            "content": quiz_content
        })

        # ⑥ Personalized Study Plan
        plan = st.session_state.get("plan", "No study plan generated.")
        sections.append({
            "title": "⑥ Personalized Study Plan",
            "content": plan.strip()
        })

        # ⑦ Related Resources
        resources = st.session_state.get("related_resources", [])
        if resources:
            resource_content = "\n\n".join([
                f"{r['title']} ({r.get('source', 'Unknown')})\n{r['summary']}\nLink: {r['link']}"
                for r in resources
            ])
        else:
            resource_content = "No resources found."
        sections.append({
            "title": "⑦ Related Resources",
            "content": resource_content
        })

        # Generate DOCX file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            export_docx(sections, tmp.name)
            docx_bytes = open(tmp.name, "rb").read()
            st.download_button(
                label="⬇️ Download Word Report",
                data=docx_bytes,
                file_name="study_report.docx"
            )
