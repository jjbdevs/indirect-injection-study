import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from harness.runners import run_openai, MODEL_OPENAI
from harness.scorer import score

SCENARIOS_FILE = Path(__file__).parent.parent / "scenarios" / "scenarios.json"
RESULTS_FILE   = Path(__file__).parent.parent / "results" / "results_openai.csv"
SLEEP_BETWEEN  = 1  # seconds — adjust based on your tier's rate limit

COLUMNS = [
    "scenario_id", "model", "payload_source", "carrier_type",
    "placement", "attack_type", "success", "evidence",
    "response_text", "tool_calls",
]


def main():
    scenarios = json.loads(SCENARIOS_FILE.read_text(encoding="utf-8"))
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    write_header = not RESULTS_FILE.exists()
    results_fh = RESULTS_FILE.open("a", newline="", encoding="utf-8")
    writer = csv.DictWriter(results_fh, fieldnames=COLUMNS)
    if write_header:
        writer.writeheader()

    completed = 0
    failed = 0

    for i, scenario in enumerate(scenarios, 1):
        sid = scenario["scenario_id"]
        print(f"[{i}/{len(scenarios)}] {sid} ...", end=" ", flush=True)

        try:
            result = run_openai(scenario)
            scored = score(scenario, result)

            writer.writerow({
                "scenario_id":   sid,
                "model":         MODEL_OPENAI,
                "payload_source": scenario["payload_source"],
                "carrier_type":  scenario["carrier_type"],
                "placement":     scenario["placement"],
                "attack_type":   scenario["attack_type"],
                "success":       scored.success,
                "evidence":      scored.evidence,
                "response_text": result.response_text,
                "tool_calls":    json.dumps(result.tool_calls),
            })
            results_fh.flush()

            status = "ATTACK SUCCEEDED" if scored.success else "defended"
            print(status)
            completed += 1

        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

        if i < len(scenarios):
            time.sleep(SLEEP_BETWEEN)

    results_fh.close()
    print(f"\nDone. {completed} completed, {failed} failed. Results: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
