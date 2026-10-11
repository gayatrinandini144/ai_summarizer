# AI Text Summarizer (Flask + Gemini API)

A real AI web app with a Python backend. The backend sends your text to
Google's Gemini API (free tier, no credit card) and returns the summary.
No big model downloads, no torch — installs in seconds.

## 1. Get a free API key
1. Go to https://aistudio.google.com/apikey and sign in with Google
2. Click **Create API key** and copy it

## 2. Run locally (Windows Command Prompt)
```
cd path\to\ai-summarizer-web
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Open `.env` in Notepad and replace `paste_your_key_here` with your key. Then:
```
python app.py
```
Open http://127.0.0.1:5000

## 3. Deploy free on Render
1. Create a GitHub repo and push these files (the `.gitignore` keeps `.env` and `venv` out — never upload your key)
2. Go to https://render.com -> New -> **Web Service** -> connect the repo
3. Settings:
   - Runtime: **Python 3**
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Instance type: **Free** (check Render's current free-plan terms)
4. Under **Environment**, add `GEMINI_API_KEY` = your key
5. Deploy. Your site goes live at `https://your-service.onrender.com`

Free instances sleep when idle, so the first visit after a while takes ~30-60s.

## Notes
- Default model is `gemini-2.5-flash`. To change it, set `GEMINI_MODEL` (locally in `.env`, on Render in Environment).
- The free API tier has rate limits; the app shows a friendly message if you hit them.
- Free-tier Gemini data may be used by Google to improve products — don't paste confidential text.

## Files
```
app.py              Flask backend + Gemini call
templates/index.html  UI
requirements.txt
Procfile            start command for hosts like Render
.env.example        copy to .env and add your key
```
