import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Groundline — Gemini Search Chat", page_icon="⟡")

MODEL_NAME = "gemini-2.5-flash"


def get_api_key():
    # Works both locally (.env / environment variable) and on Streamlit
    # Community Cloud (st.secrets, set in the app's Settings > Secrets).
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.environ.get("GEMINI_API_KEY")


def get_client():
    api_key = get_api_key()
    if not api_key:
        st.error(
            "GEMINI_API_KEY is not set. Add it locally in a .env file, or in "
            "Streamlit Cloud under App settings → Secrets."
        )
        st.stop()
    return genai.Client(api_key=api_key)


def ask_gemini(message: str):
    client = get_client()
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(tools=[grounding_tool])

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=message,
        config=config,
    )

    answer_text = response.text or ""

    sources = []
    try:
        candidate = response.candidates[0]
        grounding_metadata = getattr(candidate, "grounding_metadata", None)
        if grounding_metadata and grounding_metadata.grounding_chunks:
            for chunk in grounding_metadata.grounding_chunks:
                web = getattr(chunk, "web", None)
                if web and web.uri:
                    sources.append({"title": web.title or web.uri, "uri": web.uri})
    except (IndexError, AttributeError):
        pass

    return answer_text, sources


# ---------- UI ----------

st.title("⟡ Groundline")
st.caption(f"{MODEL_NAME} · search grounding on")

if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": ..., "content": ..., "sources": [...]}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            st.caption("Sources:")
            for s in msg["sources"]:
                st.markdown(f"- [{s['title']}]({s['uri']})")

prompt = st.chat_input("Ask Groundline anything…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching + thinking…"):
            try:
                answer, sources = ask_gemini(prompt)
            except Exception as e:
                answer, sources = f"Gemini request failed: {e}", []

        st.write(answer)
        if sources:
            st.caption("Sources:")
            for s in sources:
                st.markdown(f"- [{s['title']}]({s['uri']})")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )