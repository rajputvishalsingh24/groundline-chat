import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types

load_dotenv()  # reads variables from a local .env file, if present

app = Flask(__name__)

# The client reads GEMINI_API_KEY from the environment automatically,
# but we pass it explicitly here so a missing key gives a clear error.
API_KEY = os.environ.get("GEMINI_API_KEY")

MODEL_NAME = "gemini-2.5-flash"  # real, currently-available model name


def get_client():
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file or export it "
            "in your terminal before running the app."
        )
    return genai.Client(api_key=API_KEY)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message is empty."}), 400

    try:
        client = get_client()

        # Google Search grounding tool - this is the real, current way
        # to enable web search for a Gemini response.
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        config = types.GenerateContentConfig(
            tools=[grounding_tool],
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config=config,
        )

        answer_text = response.text or ""

        # Pull out grounding sources (the pages Gemini actually searched/used)
        sources = []
        try:
            candidate = response.candidates[0]
            grounding_metadata = getattr(candidate, "grounding_metadata", None)
            if grounding_metadata and grounding_metadata.grounding_chunks:
                for chunk in grounding_metadata.grounding_chunks:
                    web = getattr(chunk, "web", None)
                    if web and web.uri:
                        sources.append({
                            "title": web.title or web.uri,
                            "uri": web.uri,
                        })
        except (IndexError, AttributeError):
            pass

        return jsonify({"answer": answer_text, "sources": sources})

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Gemini request failed: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
