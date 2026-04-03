import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────────────────
#  Paste your Gemini API key here (from aistudio.google.com)
# ─────────────────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY")


# ─────────────────────────────────────────────────────────────
#  SETTINGS — try changing MAX_MESSAGES to see the difference!
# ─────────────────────────────────────────────────────────────
MODEL_NAME    = "gemini-2.5-flash"
MAX_MESSAGES  = 6   # 6 messages = 3 back-and-forth exchanges remembered


def get_model():
    """Configure Gemini and return the model (not a chat session)."""
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction="You are a helpful assistant. Be concise and friendly."
    )


def send_message(model, history, user_input):
    """
    Send a message WITH a trimmed history so the AI only
    sees the last MAX_MESSAGES messages — nothing more.

    HOW IT WORKS:
    Instead of using a persistent chat session (which keeps
    everything), we manually pass only the recent history each
    time. This gives us real, reliable memory control.
    """

    # Add the new user message to our history list
    history.append({
        "role": "user",
        "parts": [user_input]
    })

    # Trim: keep only the last MAX_MESSAGES messages
    # This is the slice that controls what the AI "remembers"
    trimmed = history[-MAX_MESSAGES:]

    # Start a fresh chat each time, but seed it with trimmed history
    chat = model.start_chat(history=trimmed[:-1])  # all but the last message
    response = chat.send_message(trimmed[-1]["parts"][0])  # send the last message
    reply = response.text

    # Add Gemini's reply to our full history
    history.append({
        "role": "model",
        "parts": [reply]
    })

    return reply, history


def main():
    print("=" * 52)
    print(f"  Gemini Chatbot  |  remembers last {MAX_MESSAGES // 2} exchanges")
    print("  'quit' = exit   |  'clear' = wipe memory")
    print("  'memory' = see what the AI currently knows")
    print("=" * 52)

    try:
        model = get_model()
        print("\nConnected! Start chatting.\n")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Check your API key.")
        return

    history = []   # our full conversation log

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Bye!")
            break

        if user_input.lower() == "clear":
            history = []
            print("--- Memory wiped ---\n")
            continue

        # Show what the AI currently "sees" in its memory
        if user_input.lower() == "memory":
            visible = history[-MAX_MESSAGES:]
            print(f"\n--- AI currently sees {len(visible)} messages ---")
            for i, msg in enumerate(visible):
                role = "You" if msg["role"] == "user" else "Gemini"
                print(f"  [{i+1}] {role}: {msg['parts'][0][:60]}...")
            print()
            continue

        try:
            reply, history = send_message(model, history, user_input)

            print(f"\nGemini: {reply}")

            total   = len(history)
            visible = min(total, MAX_MESSAGES)
            print(f"  [Seeing {visible}/{total} messages — oldest are forgotten]\n")

        except Exception as e:
            print(f"\nERROR: {e}\n")


if __name__ == "__main__":
    main()