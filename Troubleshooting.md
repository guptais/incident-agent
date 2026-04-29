## Troubleshooting

**`ModuleNotFoundError`**
Virtual environment isn't activated. Run `source .venv/bin/activate` — confirm `(.venv)` appears in your prompt.

**`Connection refused http://localhost:11434`**
Ollama server isn't running. Run `ollama serve` in a separate terminal, or open the Ollama Mac app.

**`403 Forbidden` from LangSmith**
`load_dotenv()` must be the first call in `incident_agent.py`, before any other imports. Check your `.env` has `LANGSMITH_API_KEY` set.

**`Ollama returned empty response`**
Tool calling reliability issue with the local model. Switch to `llama3.1` or `qwen2.5` — pull with `ollama pull qwen2.5` and update the model name in `srebuddy.py`.

**Empty incident summary**
Check `AgentState` uses `:` not `=` for the messages field:
```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # colon, not equals
```