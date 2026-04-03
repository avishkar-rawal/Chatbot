import os
import streamlit as st
import google.generativeai as genai

# ─────────────────────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────────────────────
MODEL_NAME   = "gemini-2.5-flash"
MAX_MESSAGES = 6   # 3 back-and-forth exchanges remembered

# ─────────────────────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Gemini Chatbot", page_icon="💬")
st.title("💬 Gemini Chatbot")
st.caption(f"Remembers last {MAX_MESSAGES // 2} exchanges")

# ─────────────────────────────────────────────────────────────
#  Load API key from Streamlit Secrets (set on streamlit.io)
# ─────────────────────────────────────────────────────────────
API_KEY = st.secrets.get("API_KEY") or os.getenv("API_KEY")

if not API_KEY:
    st.error("API key not found. Add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

# ─────────────────────────────────────────────────────────────
#  Initialize model and chat history in session state
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction="You are a helpful assistant. Be concise and friendly."
    )

model = get_model()

if "history" not in st.session_state:
    st.session_state.history = []   # full conversation log

# ─────────────────────────────────────────────────────────────
#  Display chat history
# ─────────────────────────────────────────────────────────────
for msg in st.session_state.history:
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(msg["parts"][0])

# ─────────────────────────────────────────────────────────────
#  Handle new input
# ─────────────────────────────────────────────────────────────
if user_input := st.chat_input("Type a message..."):

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add to history
    st.session_state.history.append({"role": "user", "parts": [user_input]})

    # Trim to last MAX_MESSAGES
    trimmed = st.session_state.history[-MAX_MESSAGES:]

    # Call Gemini
    try:
        chat = model.start_chat(history=trimmed[:-1])
        response = chat.send_message(trimmed[-1]["parts"][0])
        reply = response.text
    except Exception as e:
        reply = f"Error: {e}"

    # Show and store reply
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.history.append({"role": "model", "parts": [reply]})

# ─────────────────────────────────────────────────────────────
#  Sidebar: clear memory button
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")
    if st.button("🗑️ Clear memory"):
        st.session_state.history = []
        st.rerun()
    total   = len(st.session_state.history)
    visible = min(total, MAX_MESSAGES)
    st.caption(f"Seeing {visible}/{total} messages")