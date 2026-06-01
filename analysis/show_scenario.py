"""
Look up the recorded raw results for a single scenario across all 3 models and print
them cleanly to the terminal. Designed for projector use during the talk or for
quick inspection while writing case studies.

Usage:
    python3 analysis/show_scenario.py              # defaults to sc_021
    python3 analysis/show_scenario.py sc_071       # any scenario id
    python3 analysis/show_scenario.py sc_017 -v    # also print full carrier content
"""

import argparse
import csv
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCENARIOS_FILE = ROOT / "scenarios" / "scenarios.json"
PAYLOADS_FILE  = ROOT / "payloads" / "payloads.json"
RESULTS_FILE   = ROOT / "results" / "results.csv"

WIDTH = 80

MODEL_LABELS = {
    "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
    "gpt-4o-mini":                "GPT-4o-mini",
    "gemini-2.5-flash":           "Gemini 2.5 Flash",
}


def hr(char: str = "="):
    print(char * WIDTH)


def centered(text: str, char: str = " "):
    pad = (WIDTH - len(text)) // 2
    print(char * pad + text + char * (WIDTH - pad - len(text)))


def banner(text: str):
    print()
    hr()
    centered(text)
    hr()


def section(label: str):
    print()
    hr("-")
    print(f"  {label}")
    hr("-")


def wrap_block(text: str, prefix: str = "  | "):
    for raw_line in (text or "").splitlines() or [""]:
        wrapped = textwrap.wrap(raw_line, width=WIDTH - len(prefix), replace_whitespace=False) or [""]
        for line in wrapped:
            print(f"{prefix}{line}")


def describe_attacker_goal(success_signal: dict) -> str:
    t = success_signal["type"]
    if t == "tool_call":
        target = success_signal["tool_name"]
        needle = success_signal.get("args_must_contain", "")
        return f"Call the {target}() tool with arguments containing '{needle}'"
    if t == "output_string":
        return f"Get the model to include the string '{success_signal['must_contain']}' in its response"
    if t == "llm_judge":
        return success_signal["criterion"]
    return "Unknown attacker goal"


def show_scenario(sid: str, verbose: bool):
    scenarios = json.loads(SCENARIOS_FILE.read_text(encoding="utf-8"))
    scenario = next((s for s in scenarios if s["scenario_id"] == sid), None)
    if not scenario:
        raise SystemExit(f"Scenario {sid!r} not found in scenarios.json")

    payloads = json.loads(PAYLOADS_FILE.read_text(encoding="utf-8"))
    payload = next((p for p in payloads if p["payload_id"] == scenario["payload_id"]), None)
    if not payload:
        raise SystemExit(f"Payload {scenario['payload_id']!r} not found in payloads.json")

    with RESULTS_FILE.open(encoding="utf-8") as f:
        result_rows = [r for r in csv.DictReader(f) if r["scenario_id"] == sid]
    if not result_rows:
        raise SystemExit(f"No results found for {sid!r} in results.csv")

    # ---- scenario header ----
    banner(f"RAW RESULTS  -  {sid}")
    print()
    print(f"  Scenario ID:    {scenario['scenario_id']}")
    print(f"  Carrier type:   {scenario['carrier_type']}")
    print(f"  Placement:      {scenario['placement']}")
    print(f"  Attack type:    {scenario['attack_type']}")
    print(f"  Payload:        {payload['payload_id']}  ({payload['category']})  -  {payload['name']}")
    print(f"  Payload source: {scenario['payload_source']}")
    print()
    print(f"  User's benign task:")
    print(f"    \"{scenario['user_task']}\"")
    print()
    print(f"  What the attacker wanted:")
    for line in textwrap.wrap(describe_attacker_goal(scenario["success_signal"]), width=WIDTH - 6):
        print(f"    {line}")

    # ---- injection text ----
    section("INJECTION EMBEDDED IN THE CARRIER")
    wrap_block(payload["embedded_text"])

    # ---- optional full carrier ----
    if verbose:
        section("FULL CARRIER CONTENT THE MODEL SAW")
        wrap_block(scenario["carrier_content"])

    # ---- per-model results ----
    for row in result_rows:
        model_label = MODEL_LABELS.get(row["model"], row["model"])
        det_verdict   = "COMPROMISED" if row["success"]       == "True" else "DEFENDED"
        judge_verdict = "COMPROMISED" if row["judge_success"] == "True" else "DEFENDED"
        agreement     = "agree" if row["agreement"] == "True" else "DISAGREE"

        section(f"MODEL:  {model_label}  [{row['model']}]")

        print()
        print(f"  Response text  ({len(row['response_text'])} chars):")
        wrap_block(row["response_text"] or "(no text response)")

        tool_calls = json.loads(row["tool_calls"] or "[]")
        if tool_calls:
            print()
            print(f"  Tool calls  ({len(tool_calls)}):")
            for tc in tool_calls:
                args_preview = json.dumps(tc.get("args", {}))[:WIDTH - 12]
                print(f"  | {tc['name']}({args_preview})")
        else:
            print()
            print(f"  Tool calls:  none")

        print()
        print(f"  >>>  Deterministic verdict:  {det_verdict}")
        print(f"       Deterministic evidence: {row['evidence'][:WIDTH - 30]}")
        print(f"  >>>  Sonnet judge verdict:   {judge_verdict}  ({agreement} with deterministic)")
        if row["judge_evidence"]:
            print(f"       Judge evidence:")
            for line in textwrap.wrap(row["judge_evidence"], width=WIDTH - 10):
                print(f"         {line}")

    # ---- final cross-model summary ----
    banner("CROSS-MODEL SUMMARY")
    print()
    print(f"  {'Model':<22}  {'Deterministic':<14}  {'Judge':<14}  {'Agreement':<10}")
    print(f"  {'-'*22}  {'-'*14}  {'-'*14}  {'-'*10}")
    for row in result_rows:
        model_label = MODEL_LABELS.get(row["model"], row["model"])
        det_verdict   = "COMPROMISED" if row["success"]       == "True" else "DEFENDED"
        judge_verdict = "COMPROMISED" if row["judge_success"] == "True" else "DEFENDED"
        agreement     = "agree" if row["agreement"] == "True" else "DISAGREE"
        print(f"  {model_label:<22}  {det_verdict:<14}  {judge_verdict:<14}  {agreement:<10}")
    print()
    fell = sum(1 for r in result_rows if r["judge_success"] == "True")
    print(f"  MODELS COMPROMISED (judge):  {fell} / {len(result_rows)}")
    print()
    hr()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario_id", nargs="?", default="sc_021",
                        help="Scenario ID to inspect (default: sc_021)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Also print the full carrier content the model saw")
    args = parser.parse_args()

    show_scenario(args.scenario_id, args.verbose)


if __name__ == "__main__":
    main()
