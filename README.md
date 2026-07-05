# Groundline — Gemini Search Chat

A small Flask web app: a chat interface that sends your question to Gemini with
Google Search grounding turned on, so answers can be checked against live web
results. Sources used are shown as chips under each answer.

## About the original script

Your uploaded script called `client.interactions.create(model='models/gemini-3.5-flash', ...)`.
That method and model name aren't part of the public `google-genai` SDK, so it
wouldn't run as-is. This app uses the real, current calls:
`client.models.generate_content(...)` with `model="gemini-2.5-flash"` and a
`google_search` tool — same idea (search-grounded generation), working code.

## Project structure

```
gemini-search-chat/
├── app.py              # Flask backend, calls the Gemini API
├── requirements.txt    # Python dependencies
├── .env.example        # Copy to .env and add your API key
├── .gitignore
├── templates/
│   └── index.html      # Chat page
└── static/
    ├── style.css
    └── script.js
```

## Setup

1. Get a Gemini API key from https://aistudio.google.com/apikey
2. Copy `.env.example` to `.env` and paste your key in:
   ```
   GEMINI_API_KEY=your_actual_key
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.

## Pushing to GitHub

```
git init
git add .
git commit -m "Initial commit: Groundline chat app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

`.env` is already excluded via `.gitignore`, so your API key won't be committed.
