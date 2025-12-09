import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Check authentication
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first!")
    st.stop()

# Sidebar user info
with st.sidebar:
    st.write(f"User: {st.session_state.username}")
    st.write(f"Role: {st.session_state.role.upper()}")

st.title("AI Chatbot Assistant")

# Initialize OpenAI client
client = OpenAI(api_key='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')

# Initialize session state
if "custom_system_prompt" not in st.session_state:
    st.session_state.custom_system_prompt = "You are a helpful assistant specializing in cybersecurity, IT support, and general technical questions. Provide clear, accurate, and actionable advice."

if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": st.session_state.custom_system_prompt}]

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Say Something")

if prompt:
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Send to OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        temperature=1,
        stream=True
    )

    # Display streaming assistant output
    with st.chat_message("assistant"):
        container = st.empty()
        full_reply = ""

        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta.content:
                full_reply += delta.content
                container.markdown(full_reply)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_reply})

# Sidebar controls
with st.sidebar:
    st.markdown("---")
    st.subheader("Customize System Prompt")
    
    # Default system prompt
    default_prompt = "You are a helpful assistant specializing in cybersecurity, IT support, and general technical questions. Provide clear, accurate, and actionable advice."
    
    # Initialize custom prompt in session state if not exists
    if "custom_system_prompt" not in st.session_state:
        st.session_state.custom_system_prompt = default_prompt
    
    # Text area for custom prompt
    custom_prompt = st.text_area(
        "System Prompt:",
        value=st.session_state.custom_system_prompt,
        height=150,
        help="Customize how the AI assistant behaves and responds"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Apply", use_container_width=True):
            st.session_state.custom_system_prompt = custom_prompt
            # Update or add system message at the beginning
            if len(st.session_state.messages) > 0 and st.session_state.messages[0].get("role") == "system":
                st.session_state.messages[0] = {"role": "system", "content": custom_prompt}
            else:
                st.session_state.messages.insert(0, {"role": "system", "content": custom_prompt})
            st.success("Prompt updated!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.custom_system_prompt = default_prompt
            # Update or add system message at the beginning
            if len(st.session_state.messages) > 0 and st.session_state.messages[0].get("role") == "system":
                st.session_state.messages[0] = {"role": "system", "content": default_prompt}
            else:
                st.session_state.messages.insert(0, {"role": "system", "content": default_prompt})
            st.success("Prompt reset!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("Chat Controls")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.info("This chatbot uses OpenAI's GPT-4o-mini to answer your questions.")
    
    # Display message count
    st.metric("Messages", len(st.session_state.messages))
