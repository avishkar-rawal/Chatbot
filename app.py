import os
import streamlit as st
import google.generativeai as genai

# ─────────────────────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────────────────────
MODEL_NAME   = "gemini-2.5-flash"
MAX_MESSAGES = 6

# ─────────────────────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Gemini Chatbot", page_icon="✨", layout="centered")

# ─────────────────────────────────────────────────────────────
#  Custom CSS + JS — particles, animations, dark theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base dark background ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0a0a1a !important;
    color: #e0e0ff !important;
}

[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* ── Particle canvas ── */
#particle-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
    pointer-events: none;
}

/* ── Push content above canvas ── */
[data-testid="stAppViewContainer"] > * {
    position: relative;
    z-index: 1;
}

/* ── Title ── */
h1 {
    color: #a78bfa !important;
    text-align: center;
    font-size: 2rem !important;
    letter-spacing: 2px;
    text-shadow: 0 0 20px rgba(167,139,250,0.5);
}

/* ── Chat message fade-in ── */
[data-testid="stChatMessage"] {
    animation: fadeSlideIn 0.4s ease forwards;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(167,139,250,0.15) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px);
    margin-bottom: 8px;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(167,139,250,0.3) !important;
    color: #e0e0ff !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 12px rgba(167,139,250,0.25) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(15,15,35,0.85) !important;
    border-right: 1px solid rgba(167,139,250,0.15) !important;
    backdrop-filter: blur(12px);
}

/* ── Sidebar button ── */
[data-testid="stSidebar"] button {
    background: rgba(167,139,250,0.12) !important;
    border: 1px solid rgba(167,139,250,0.3) !important;
    color: #a78bfa !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] button:hover {
    background: rgba(167,139,250,0.25) !important;
    box-shadow: 0 0 12px rgba(167,139,250,0.3) !important;
}

/* ── Caption / muted text ── */
[data-testid="stCaptionContainer"] p, small {
    color: rgba(167,139,250,0.6) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(167,139,250,0.3); border-radius: 3px; }
</style>

<canvas id="particle-canvas"></canvas>

<script>
(function() {
    const canvas = document.getElementById('particle-canvas');
    const ctx    = canvas.getContext('2d');
    let W, H, stars = [];

    function resize() {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }

    function randomStar() {
        return {
            x:     Math.random() * W,
            y:     Math.random() * H,
            r:     Math.random() * 1.5 + 0.3,
            alpha: Math.random(),
            speed: Math.random() * 0.003 + 0.001,
            drift: (Math.random() - 0.5) * 0.15
        };
    }

    function init() {
        resize();
        stars = Array.from({ length: 160 }, randomStar);
    }

    function draw() {
        ctx.clearRect(0, 0, W, H);
        stars.forEach(s => {
            s.alpha += s.speed;
            if (s.alpha > 1) { s.alpha = 0; s.x = Math.random() * W; s.y = Math.random() * H; }
            s.x += s.drift;
            if (s.x < 0) s.x = W;
            if (s.x > W) s.x = 0;

            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(180, 160, 255, ${s.alpha * 0.85})`;
            ctx.fill();
        });

        if (Math.random() < 0.002) {
            const sx   = Math.random() * W;
            const sy   = Math.random() * H * 0.5;
            const grad = ctx.createLinearGradient(sx, sy, sx + 80, sy + 30);
            grad.addColorStop(0, 'rgba(200,180,255,0.9)');
            grad.addColorStop(1, 'rgba(200,180,255,0)');
            ctx.beginPath();
            ctx.moveTo(sx, sy);
            ctx.lineTo(sx + 80, sy + 30);
            ctx.strokeStyle = grad;
            ctx.lineWidth   = 1.5;
            ctx.stroke();
        }

        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
    init();
    draw();
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  Title
# ─────────────────────────────────────────────────────────────
st.title("✨ Gemini Chatbot")
st.caption(f"Remembers last {MAX_MESSAGES // 2} exchanges")

# ─────────────────────────────────────────────────────────────
#  API key
# ─────────────────────────────────────────────────────────────
API_KEY = st.secrets.get("API_KEY") or os.getenv("API_KEY")

if not API_KEY:
    st.error("API key not found. Add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

# ─────────────────────────────────────────────────────────────
#  Model
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
    st.session_state.history = []

# ─────────────────────────────────────────────────────────────
#  Display chat history
# ─────────────────────────────────────────────────────────────
for msg in st.session_state.history:
    role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(msg["parts"][0])

# ─────────────────────────────────────────────────────────────
#  Handle input
# ─────────────────────────────────────────────────────────────
if user_input := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.history.append({"role": "user", "parts": [user_input]})
    trimmed = st.session_state.history[-MAX_MESSAGES:]

    try:
        chat     = model.start_chat(history=trimmed[:-1])
        response = chat.send_message(trimmed[-1]["parts"][0])
        reply    = response.text
    except Exception as e:
        reply = f"Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.history.append({"role": "model", "parts": [reply]})

# ─────────────────────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ✨ Controls")
    if st.button("🗑️ Clear memory"):
        st.session_state.history = []
        st.rerun()
    total   = len(st.session_state.history)
    visible = min(total, MAX_MESSAGES)
    st.caption(f"Seeing {visible}/{total} messages")