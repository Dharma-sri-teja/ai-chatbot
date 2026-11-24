
import streamlit as st

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# -------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------

st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# -------------------------------
# 2. AI MODEL CONFIGURATION
# -------------------------------

llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0.7
)

# -------------------------------
# 3. PROMPT CONFIGURATION
# -------------------------------

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful AI assistant. "
        "Give clear, simple and accurate answers."
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

chain = prompt | llm

# -------------------------------
# 4. SESSION STATE
# -------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# -------------------------------
# 5. SIDEBAR
# -------------------------------

st.sidebar.title("🤖 Chat Manager")

st.sidebar.write(
    f"Messages: {len(st.session_state.chat_history) // 2}"
)

if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.chat_count += 1
    st.rerun()

if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

st.sidebar.divider()

st.sidebar.caption(
    "Powered by Python, LangChain and Ollama"
)

# -------------------------------
# 6. MAIN CHAT INTERFACE
# -------------------------------

st.title("🤖 My AI Chatbot")

st.caption(
    "Your personal AI assistant powered by Llama 3.2"
)

# Display previous messages

for message in st.session_state.chat_history:

    if isinstance(message, HumanMessage):
        role = "user"
    else:
        role = "assistant"

    with st.chat_message(role):
        st.markdown(message.content)

# -------------------------------
# 7. USER INPUT
# -------------------------------

user_input = st.chat_input("Ask me anything...")

if user_input:

    with st.chat_message("user"):
        st.markdown(user_input)

    try:

        with st.chat_message("assistant"):

            with st.spinner("AI is thinking..."):

                response = chain.invoke({
                    "chat_history": st.session_state.chat_history,
                    "question": user_input
                })

            st.markdown(response.content)

        # Save conversation

        st.session_state.chat_history.append(
            HumanMessage(content=user_input)
        )

        st.session_state.chat_history.append(
            AIMessage(content=response.content)
        )

        st.rerun()

    except Exception as e:

        st.error(f"Something went wrong: {e}")
