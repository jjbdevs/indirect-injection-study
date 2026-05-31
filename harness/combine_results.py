import csv
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / "results"
INPUTS = [
    "results_claude_judged.csv",
    "results_openai_judged.csv",
    "results_gemini_judged.csv",
]
OUTPUT = "results.csv"


def main():
    out_path = RESULTS_DIR / OUTPUT
    all_rows = []
    fieldnames = None

    for name in INPUTS:
        path = RESULTS_DIR / name
        if not path.exists():
            print(f"WARN: {name} not found, skipping")
            continue
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if fieldnames is None:
                fieldnames = reader.fieldnames
            elif reader.fieldnames != fieldnames:
                raise ValueError(f"{name} has different columns than first input")
            rows = list(reader)
            print(f"  {name}: {len(rows)} rows")
            all_rows.extend(rows)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
