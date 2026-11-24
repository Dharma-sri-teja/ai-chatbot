
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

import database


st.set_page_config(
    page_title="My AI Chatbot",
    page_icon=":material/smart_toy:",
    layout="centered",
)


database.init_db()
st.session_state.setdefault("chat_error", None)
st.session_state.setdefault("chat_notice", None)


@st.cache_resource
def get_chat_chain():
    llm = ChatOllama(model="llama3.2:1b", temperature=0.7)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful, accurate AI assistant. "
                "Answer clearly and concisely, organize complex answers with headings "
                "or lists when useful, and admit uncertainty rather than inventing facts.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    return prompt | llm


def get_ai_response_content(response):
    content = getattr(response, "content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                text_parts.append(part["text"])
        return "".join(text_parts).strip()
    return ""


def friendly_error(error):
    message = str(error).lower()
    if "connection" in message or "refused" in message:
        return "Ollama is not reachable. Make sure Ollama is running and llama3.2:1b is installed."
    if "model" in message and ("not found" in message or "does not exist" in message):
        return "The llama3.2:1b model is not installed. Run: ollama pull llama3.2:1b"
    return "The AI could not complete your request. Please try again."


def export_txt(conversation, messages):
    lines = [conversation["title"], "=" * len(conversation["title"]), ""]
    for message in messages:
        label = "You" if message["role"] == "user" else "Assistant"
        lines.extend([f"{label}: {message['content']}", ""])
    return "\n".join(lines)


def export_markdown(conversation, messages):
    lines = [f"# {conversation['title']}", ""]
    for message in messages:
        label = "**You**" if message["role"] == "user" else "**Assistant**"
        lines.extend([f"{label}: {message['content']}", ""])
    return "\n".join(lines)


conversations = database.get_conversations()
if "active_conversation_id" not in st.session_state:
    if conversations:
        st.session_state.active_conversation_id = conversations[0]["id"]
    else:
        st.session_state.active_conversation_id = database.create_conversation()
        conversations = database.get_conversations()

active_id = st.session_state.active_conversation_id
if active_id not in {conversation["id"] for conversation in conversations}:
    active_id = conversations[0]["id"] if conversations else database.create_conversation()
    st.session_state.active_conversation_id = active_id
    conversations = database.get_conversations()

active_conversation = next(
    conversation for conversation in conversations if conversation["id"] == active_id
)

with st.sidebar:
    st.title("AI chatbot")
    st.caption("A local assistant powered by Llama 3.2")
    st.divider()

    if st.button("New chat", icon=":material/add:", width="stretch"):
        st.session_state.active_conversation_id = database.create_conversation()
        st.rerun()

    conversation_by_id = {
        conversation["id"]: conversation
        for conversation in conversations
    }
    conversation_ids = list(conversation_by_id)

    if conversation_ids:
        selected_id = st.selectbox(
            "Conversations",
            conversation_ids,
            index=conversation_ids.index(active_id),
            format_func=lambda conversation_id: (
                f"{conversation_by_id[conversation_id]['title']} (#{conversation_id})"
            ),
            key="conversation_select_id",
        )
        if selected_id != active_id:
            st.session_state.active_conversation_id = selected_id
            st.rerun()

    st.divider()
    messages_for_export = database.get_messages(active_id)
    st.download_button(
        "Export TXT",
        export_txt(active_conversation, messages_for_export),
        file_name=f"conversation-{active_id}.txt",
        mime="text/plain",
        icon=":material/download:",
        width="stretch",
        disabled=not messages_for_export,
    )
    st.download_button(
        "Export Markdown",
        export_markdown(active_conversation, messages_for_export),
        file_name=f"conversation-{active_id}.md",
        mime="text/markdown",
        icon=":material/download:",
        width="stretch",
        disabled=not messages_for_export,
    )

    st.divider()
    if st.button(
        "Delete conversation",
        icon=":material/delete:",
        width="stretch",
        type="secondary",
        disabled=len(conversations) == 0,
    ):
        database.delete_conversation(active_id)
        remaining = database.get_conversations()
        st.session_state.active_conversation_id = (
            remaining[0]["id"] if remaining else database.create_conversation()
        )
        st.rerun()

    st.divider()
    st.markdown("### About")
    st.caption("Built with Python, Streamlit, LangChain, Ollama and SQLite.")


if st.session_state.chat_error:
    st.error(st.session_state.chat_error, icon=":material/error:")
    st.session_state.chat_error = None
if st.session_state.chat_notice:
    st.warning(st.session_state.chat_notice)
    st.session_state.chat_notice = None

st.title("My AI Chatbot")
st.caption("Your personal AI assistant powered by Llama 3.2")
st.divider()

stored_messages = database.get_messages(active_id)

if not stored_messages:
    st.markdown("### Hello! Welcome.")
    st.write("I'm your AI assistant. Ask me anything and I'll try my best to help.")
    suggestions = st.pills(
        "Try asking",
        [
            "Explain Python in simple words",
            "What is artificial intelligence?",
            "Explain machine learning",
            "Write a Python program to reverse a string",
        ],
        label_visibility="collapsed",
    )
else:
    suggestions = None

for message in stored_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything...", submit_mode="disable")

if prompt:
    user_input = prompt
elif not stored_messages and suggestions:
    user_input = suggestions
else:
    user_input = None

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    recent_messages = stored_messages[-10:]
    chat_history = []
    for message in recent_messages:
        if message["role"] == "user":
            chat_history.append(HumanMessage(content=message["content"]))
        else:
            chat_history.append(AIMessage(content=message["content"]))

    database.add_message(active_id, "user", user_input)

    if not stored_messages:
        title = user_input[:45].rstrip()
        if len(user_input) > 45:
            title += "..."
        database.update_conversation_title(active_id, title)

    with st.chat_message("assistant"):
        try:
            with st.spinner("AI is thinking..."):
                response = get_chat_chain().invoke(
                    {
                        "chat_history": chat_history,
                        "question": user_input,
                    }
                )
            answer = get_ai_response_content(response)
            if not answer:
                st.session_state.chat_notice = (
                    "The AI returned an empty response. Please try asking again."
                )
            else:
                st.markdown(answer)
                database.add_message(active_id, "assistant", answer)
        except Exception as error:
            st.session_state.chat_error = friendly_error(error)
            print(f"Chatbot error: {error}")

    st.rerun()
