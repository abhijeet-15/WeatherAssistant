import streamlit as st
from index import ask_llm_with_tool
from llm.prompt_manager import PromptManager
from llm.factory import build_client, select_provider
from tools import TOOL_SCHEMAS, AVAILABLE_TOOLS

prompt_manager = PromptManager()

with st.sidebar:
    st.header("About this project")
    st.markdown(prompt_manager.build_greeting())

    st.divider()

    st.subheader("Provider")
    try:
        provider = select_provider()
        model = provider.model
        client = provider.name
        st.success(f"Provider: {provider.name}\nmodel: {model}\n client={client}")
    except RuntimeError as e:
        st.error(f"error: {e}")

    st.divider()

    st.subheader("Jinja system Prompt")
    st.caption("The agent uses the system prompt to answer the questions.")

    with st.expander("Preview rendered prompt", expanded =False):
        st.code(prompt_manager.build_system_prompt(tools_list=TOOL_SCHEMAS))

    st.divider()

    if st.button("Restart"):
        st.session_state.chat_log = []
        st.rerun()

st.title("Weather assistant")

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

for entry in st.session_state.chat_log:
    if entry.get("content"):
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])

prompt = st.chat_input("Ask the agent about weather information")

if prompt:
    st.session_state.chat_log.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.write(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask_llm_with_tool(messages=st.session_state.chat_log)
                st.write(answer)
                
                st.session_state.chat_log.append({
                    "role": "assistant",
                    "content": answer
                })
                
            except Exception as e:
                st.error(f"Agent encountered an error: {e}")