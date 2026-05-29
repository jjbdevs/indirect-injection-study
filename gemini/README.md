# Gemini runner

Runs each scenario from `../scenarios.json` through a Gemini model with mock tools,
then scores the results against each payload's `success_signal`.

## Setup

```bash
pip install google-genai python-dotenv
cp .env.example .env
# then edit .env and paste your Gemini API key
```

`.env` keys:

- `GEMINI_API_KEY` — from https://aistudio.google.com/app/apikey
- `GEMINI_MODEL` — defaults to `gemini-2.0-flash-lite`. Use `gemini-2.5-flash-lite`
  if you're on the free tier (the `-lite` variant of 2.0 has no free quota).

## Run

```bash
# From the repo root, generate scenarios.json if it isn't already there
python3 generate_scenarios.py

# From this folder, run the agent across all 100 scenarios
python3 run_agent.py              # ~10-15 min on free-tier RPM
python3 run_agent.py --limit 5    # smoke-test with 5

# Score everything
python3 score_results.py          # writes results/scored.csv
```

`run_agent.py` is resumable: if it crashes or you stop it, re-running picks up only
the scenarios that haven't completed successfully. Use `--rerun` to start over.

## What lives where

- `run_agent.py` — the agent loop and mock tool definitions
- `score_results.py` — applies each scenario's `success_signal` (tool_call / output_string / llm_judge)
- `results/raw_results.jsonl` — one line per scenario, includes tool calls + final text
- `results/scored.csv` — flat table for analysis
