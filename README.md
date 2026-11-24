# AI Chatbot

A locally running AI chatbot built with Python, Streamlit, LangChain, Ollama,
and SQLite.

## Features

- Local responses using Llama 3.2 (1B)
- Conversation context and persistent chat history
- Multiple saved conversations
- Conversation selection and deletion
- TXT and Markdown export
- Friendly Ollama connection and model errors
- SQLite storage with automatic database setup

## Technologies

- Python
- Streamlit
- LangChain
- Ollama
- SQLite

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Dharma-sri-teja/ai-chatbot.git
   cd ai-chatbot/AI_Chatbot
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Install Ollama from https://ollama.com/ and download the model:

   ```bash
   ollama pull llama3.2:1b
   ```

5. Start the application:

   ```bash
   python -m streamlit run app.py
   ```

## Database

The application creates `chat_history.db` automatically. It stores conversation
titles, user messages, assistant responses, and timestamps locally.

## Privacy

Chat data stays on your computer and is not sent to GitHub. The database and
environment directories are excluded by `.gitignore`.
