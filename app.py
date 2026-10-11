"""
AI Text Summarizer — Flask backend + Gemini API
Run locally:  python app.py   ->  http://127.0.0.1:5000
Deploy:       gunicorn app:app  (e.g. on Render)
"""
import os
import requests
from flask import Flask, render_template, request, jsonify

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

MAX_WORDS = 8000  # protect the free API quota

LENGTH_INSTRUCTIONS = {
    "short": "in 1-2 sentences",
    "medium": "in one concise paragraph (about 3-5 sentences)",
    "long": "in a detailed summary of 2-3 paragraphs",
}
STYLE_INSTRUCTIONS = {
    "paragraph": "Write it as flowing prose.",
    "bullets": "Write it as clear bullet points, each starting with '- '.",
}


def build_prompt(text, length, style):
    return (
        f"Summarize the following text {LENGTH_INSTRUCTIONS.get(length, LENGTH_INSTRUCTIONS['medium'])}. "
        f"{STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS['paragraph'])} "
        "Keep only the key ideas, stay faithful to the text, and do not add outside information. "
        "Reply with the summary only, no preface.\n\n"
        f"TEXT:\n{text}"
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def summarize():
    if not API_KEY:
        return jsonify({"error": "Server is missing GEMINI_API_KEY. See README."}), 500

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    length = data.get("length", "medium")
    style = data.get("style", "paragraph")

    words = len(text.split())
    if words < 30:
        return jsonify({"error": "Please enter at least ~30 words."}), 400
    if words > MAX_WORDS:
        return jsonify({"error": f"Text too long. Limit is {MAX_WORDS} words."}), 400

    payload = {"contents": [{"parts": [{"text": build_prompt(text, length, style)}]}]}
    try:
        r = requests.post(
            API_URL,
            headers={"x-goog-api-key": API_KEY, "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        if r.status_code == 429:
            return jsonify({"error": "Rate limit reached (free tier). Wait a minute and retry."}), 429
        if r.status_code != 200:
            msg = r.json().get("error", {}).get("message", r.text[:200])
            return jsonify({"error": f"AI API error: {msg}"}), 502
        parts = r.json()["candidates"][0]["content"]["parts"]
        summary = "".join(p.get("text", "") for p in parts).strip()
    except (requests.RequestException, KeyError, IndexError, ValueError) as e:
        return jsonify({"error": f"Could not get a summary: {e}"}), 502

    sw = len(summary.split())
    return jsonify({
        "summary": summary,
        "original_words": words,
        "summary_words": sw,
        "reduction": round((1 - sw / words) * 100, 1),
    })


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
