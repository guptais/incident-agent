# incident-agent

A LangGraph-based incident response agent that investigates alerts by gathering evidence across multiple observability tools and synthesising a root cause analysis.

## Architecture

```
Alert (trigger)
    → LangGraph agent (LLM decides which tools to call)
    → Tools: Datadog · GitHub · Sentry
    → LLM synthesises evidence → RCA
```

Traces visible in [LangSmith](https://smith.langchain.com/).

## Setup

```bash

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in your keys
cp .env.example .env
```

## Environment variables

```
LANGSMITH_API_KEY       # from smith.langchain.com → Settings → API Keys
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=incident-agent
```

## Local model (Ollama)

This project uses a local LLM via Ollama — no API costs.

```bash
# Install Ollama
brew install ollama

# Pull the model
ollama pull llama3.1

# Start the server (keep this running in a separate terminal)
ollama serve
```

## Run

```bash
python incident_agent.py
```

