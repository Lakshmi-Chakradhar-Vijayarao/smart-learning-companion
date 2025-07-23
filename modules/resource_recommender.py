import os
import requests
import feedparser
import urllib.parse
import streamlit as st

# Fallback to os.environ if running locally
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", os.getenv("SERPAPI_KEY"))


# ─────────────── Wikipedia Summary ───────────────
def search_wikipedia(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            summary = data.get("extract", "No summary found.")
            page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
            return summary, page_url
    except Exception:
        pass
    return "Wikipedia search failed.", ""


# ─────────────── arXiv API ───────────────
def get_arxiv_papers(query):
    encoded_query = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results=2"
    try:
        feed = feedparser.parse(url)
        papers = []
        for entry in feed.entries:
            title = entry.title.replace("\n", " ").strip()
            summary = entry.summary.replace("\n", " ").strip()[:200]
            link = entry.link.strip()
            papers.append({
                "title": title,
                "summary": summary + "...",
                "link": link,
                "source": "arXiv"
            })
        return papers
    except Exception:
        return []


# ─────────────── Google Scholar via SerpAPI ───────────────
def get_google_scholar_resources(query):
    url = "https://serpapi.com/search"

    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5
    }

    try:
        res = requests.get(url, params=params, timeout=6)
        data = res.json()
        papers = []
        for item in data.get("organic_results", []):
            title = item.get("title")
            summary = item.get("snippet", "")
            link = item.get("link")
            if title and link:
                papers.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "source": "Google Scholar"
                })
            if len(papers) >= 2:
                break
        return papers
    except Exception as e:
        print(f"[SerpAPI Scholar Error] {e}")
        return []
