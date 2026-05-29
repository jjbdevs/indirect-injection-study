# Claude runner

Placeholder for the Claude version of the agent runner + scorer. The Gemini
implementation lives in `../gemini/` and is a useful reference for the contract:

- Reads `../scenarios.json` (shared with Gemini, model-agnostic).
- Exposes 5 mock tools: `send_email`, `fetch_url`, `transfer_funds`,
  `delete_files`, `post_to_social_media`. Mock tools should always return a
  generic success so the agent doesn't retry.
- For each scenario, records every tool call (name + args) plus the final text.
- Scorer reads each `success_signal` and emits a per-scenario pass/fail row.
  Signal types in the dataset: `tool_call` (18), `output_string` (4), `llm_judge` (8).

Drop `run_agent.py`, `score_results.py`, `.env`, and a `results/` folder here when ready.
