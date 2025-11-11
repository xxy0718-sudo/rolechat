# app.py
import streamlit as st
import openai
from datetime import datetime

st.set_page_config(page_title="Role-based Creative Chatbot", layout="wide", page_icon="🎭")

# -------------------------
# UI: header
# -------------------------
st.markdown("<h1 style='text-align:center'>🎭 Role-based Creative Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray'>Select a creative professional role, type your question, and get role-specific guidance.</p>", unsafe_allow_html=True)
st.write("---")

# -------------------------
# Sidebar: API key & role settings
# -------------------------
with st.sidebar:
    st.header("🔐 API & Role Settings")

    # 1) API key input (masked)
    api_key_input = st.text_input("Enter your OpenAI API key (sk-...)", type="password")
    st.caption("Tip: For deployment, put the key into Streamlit Secrets instead of typing it here.")

    # 2) choose role
    st.subheader("Choose a role")
    # default role set
    ROLE_PRESETS = {
        "🎬 Video Director": (
            "You are a professional film director. Always analyze ideas in terms of visual storytelling — use camera movement, lighting, framing, and emotional tone. "
            "Give concrete, scene-based advice and, if appropriate, shot lists or blocking notes."
        ),
        "💃 Dance Instructor": (
            "You are a dance instructor. Suggest movement choices, rhythm and dynamics, count structures, and how to express emotion through body language. "
            "Offer small exercises and step-by-step breakdowns."
        ),
        "👗 Fashion Stylist": (
            "You are a fashion stylist. Explain color palettes, materials, silhouettes, and outfit layering suited to personality and context. Provide alternatives and reference ideas."
        ),
        "🎭 Acting Coach": (
            "You are an acting coach. Teach natural emotion delivery, scene analysis, subtext, and exercises for authentic performance."
        ),
        "🖼️ Art Curator": (
            "You are an art curator. Interpret artworks, reference art-historical parallels, suggest display and conceptual approaches, and ask thoughtful critical questions."
        ),
        "🧑‍🎨 Custom Role (editable)": "Describe the role behavior here. Be specific about tone, constraints, and what to avoid."
    }

    role_choice = st.selectbox("Role", list(ROLE_PRESETS.keys()))
    # default editable content
    default_system_prompt = ROLE_PRESETS[role_choice]
    custom_role_prompt = st.text_area("Role description (system prompt)", value=default_system_prompt, height=200)

    st.markdown("---")
    st.subheader("Generation Settings")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-5-mini"], index=0)
    temperature = st.slider("Temperature (creativity)", 0.0, 1.2, 0.85)
    max_tokens = st.slider("Max tokens", 100, 1500, 600)

    st.markdown("---")
    st.caption("Built for classroom use • Not financial/advice-critical")

# -------------------------
# Set API key
# -------------------------
# Priority: typed API key -> streamlit secrets (if available) -> prompt user
if api_key_input:
    openai.api_key = api_key_input.strip()
else:
    # check secrets (works on Streamlit Cloud)
    try:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        openai.api_key = None

# -------------------------
# Main UI: input & conversation
# -------------------------
col1, col2 = st.columns([4, 1])

with col1:
    st.subheader("💬 Ask the role")
    user_input = st.text_area("Enter your question or idea:", placeholder="e.g., How can I shoot a dream sequence that feels surreal but intimate?", height=140)

    # controls
    gen_col1, gen_col2 = st.columns([1,1])
    with gen_col1:
        if st.button("Generate Response"):
            if not openai.api_key:
                st.error("OpenAI API key not provided. Enter it in the sidebar or set Streamlit Secrets.")
            elif not user_input.strip():
                st.warning("Please enter a question or idea first.")
            else:
                # prepare messages
                system_message = custom_role_prompt
                # preserve conversation history in session state
                if "conversation" not in st.session_state:
                    st.session_state.conversation = [{"role":"system","content":system_message}]
                # append user
                st.session_state.conversation.append({"role":"user","content":user_input})

                # call OpenAI ChatCompletion
                with st.spinner("Generating..."):
                    try:
                        response = openai.ChatCompletion.create(
                            model=model,
                            messages=st.session_state.conversation,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        assistant_msg = response["choices"][0]["message"]["content"]
                        # append assistant to conversation
                        st.session_state.conversation.append({"role":"assistant","content":assistant_msg})
                    except Exception as e:
                        st.error(f"API request failed: {e}")

    with gen_col2:
        if st.button("Reset Conversation"):
            st.session_state.conversation = [{"role":"system","content":custom_role_prompt}]
            st.success("Conversation reset.")

    st.markdown("---")

    # show conversation (most recent first)
    if "conversation" in st.session_state:
        for msg in reversed(st.session_state.conversation):
            if msg["role"] == "system":
                continue
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**{role_choice} (assistant):** {msg['content']}")

with col2:
    st.subheader("📘 Role Card")
    st.markdown(f"**Role:** {role_choice}")
    st.info(custom_role_prompt)

    st.markdown("---")
    st.subheader("⚙️ Tips")
    st.write("- Be specific with context (location, medium, constraints).")
    st.write("- Ask for examples or step-by-step instructions when you need practical guidance.")
    st.write("- You can edit the role prompt to make the assistant stricter or more playful.")
    st.markdown("---")
    st.subheader("🔒 Security")
    st.write("Do not paste secret documents. Keep API keys private; use Streamlit Secrets for deployment.")

# -------------------------
# Show model debug info (optional, collapsed)
# -------------------------
with st.expander("Debug / Conversation JSON (hidden)"):
    st.json(st.session_state.get("conversation", [{"role":"system","content":custom_role_prompt}]))
