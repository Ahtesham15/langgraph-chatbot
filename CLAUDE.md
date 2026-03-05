# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the app:**
```bash
# Most complete version (SQLite persistence + multi-thread + streaming)
streamlit run streamlit_frontend_database.py

# Other frontend variants
streamlit run streamlit_frontend.py           # basic, single fixed thread
streamlit run streamlit_frontend_streaming.py # streaming, single fixed thread
streamlit run streamlit_frontend_threading.py # multi-thread, in-memory only
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Environment setup:** Requires a `.env` file with `OPENAI_API_KEY`.

## Architecture

This project is a LangGraph-based chatbot with a Streamlit UI. There are two backend files and four frontend files representing an iterative build-up of features.

### Backend files

Both backends define an identical LangGraph graph structure:
- `ChatState` TypedDict with `messages: Annotated[list[BaseMessage], add_messages]`
- A single `chat_node` that calls `ChatOpenAI` and returns the response
- A compiled `chatbot` graph exported for use by frontends

The difference is the checkpointer:
- `langgraph_backend.py` — uses `InMemorySaver` (state lost on restart)
- `langgraph_database_backend.py` — uses `SqliteSaver` with `chatbot.db`; also exports `retrieve_all_threads()` to list existing conversation threads from the DB

### Frontend files (progression of features)

| File | Backend | Multi-thread | Streaming | Persistence |
|------|---------|-------------|-----------|-------------|
| `streamlit_frontend.py` | memory | no (hardcoded `thread-1`) | no | no |
| `streamlit_frontend_streaming.py` | memory | no (hardcoded `thread-1`) | yes | no |
| `streamlit_frontend_threading.py` | memory | yes (UUID threads, sidebar) | yes | no |
| `streamlit_frontend_database.py` | sqlite | yes (UUID threads, sidebar) | yes | yes |

**`streamlit_frontend_database.py`** is the most complete version. It:
- Loads existing threads from SQLite on startup via `retrieve_all_threads()`
- Uses `chatbot.stream(..., stream_mode='messages')` with `st.write_stream()` for token-level streaming
- Manages `thread_id`, `message_history`, and `chat_threads` in `st.session_state`
- Supports resuming past conversations by clicking threads in the sidebar (`load_conversation` calls `chatbot.get_state()`)

### Key LangGraph concepts used

- **Thread-based memory**: each conversation has a UUID `thread_id` passed via `config={'configurable': {'thread_id': ...}}` on every `invoke`/`stream` call
- **Checkpointing**: the checkpointer automatically persists and rehydrates message history per thread — no manual history management needed at the graph level
- **Streaming**: `chatbot.stream(..., stream_mode='messages')` yields `(message_chunk, metadata)` tuples; only `message_chunk.content` is used
