"""
Analyze results.csv across all 3 models. Produces tables to stdout and PNGs to analysis/figures/.

Uses judge_success (Sonnet 4.6) for cross-model comparison so all three models are scored
under the same methodology, not Gemini's mixed deterministic/Gemini-judge column.
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent.parent
RESULTS_FILE = ROOT / "results" / "results.csv"
FIGURES_DIR = Path(__file__).parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Display names for the 3 models, in plot order
MODEL_LABELS = {
    "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
    "gpt-4o-mini":                "GPT-4o-mini",
    "gemini-2.5-flash":           "Gemini 2.5 Flash",
}
MODEL_ORDER = list(MODEL_LABELS.values())
MODEL_COLORS = {
    "Claude Haiku 4.5": "#d4a373",   # warm tan
    "GPT-4o-mini":      "#74c69d",   # mint green
    "Gemini 2.5 Flash": "#90a8c3",   # slate blue
}


def load_data() -> pd.DataFrame:
    df = pd.read_csv(RESULTS_FILE)
    df["judge_success"] = df["judge_success"].astype(str).str.lower() == "true"
    df["success"]       = df["success"].astype(str).str.lower() == "true"
    df["model_label"]   = df["model"].map(MODEL_LABELS)
    return df


def asr_table(df: pd.DataFrame, group_cols: list, value_col: str = "judge_success") -> pd.DataFrame:
    grouped = df.groupby(group_cols)[value_col].agg(["sum", "count"])
    grouped["asr"] = grouped["sum"] / grouped["count"]
    return grouped


def print_table(title: str, table: pd.DataFrame):
    print(f"\n=== {title} ===")
    formatted = table.copy()
    formatted["asr"] = (formatted["asr"] * 100).round(1).astype(str) + "%"
    formatted = formatted.rename(columns={"sum": "successes", "count": "n", "asr": "ASR"})
    print(formatted.to_string())


def plot_overall_asr(df: pd.DataFrame):
    asr = df.groupby("model_label")["judge_success"].mean().reindex(MODEL_ORDER) * 100
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(asr.index, asr.values, color=[MODEL_COLORS[m] for m in asr.index], edgecolor="black", linewidth=0.5)

    for bar, val in zip(bars, asr.values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1, f"{val:.0f}%", ha="center", va="bottom", fontweight="bold")

    ax.set_ylabel("Attack Success Rate (%)")
    ax.set_title("Indirect Prompt Injection Susceptibility by Model\n(100 scenarios per model, Sonnet 4.6 judge)")
    ax.set_ylim(0, max(asr.values) * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    out = FIGURES_DIR / "01_overall_asr.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → saved {out.name}")


def plot_grouped(df: pd.DataFrame, group_col: str, title: str, filename: str,
                 order: list = None):
    pivot = (df.groupby([group_col, "model_label"])["judge_success"]
             .mean().unstack("model_label") * 100)
    pivot = pivot.reindex(columns=MODEL_ORDER)
    if order:
        pivot = pivot.reindex(order)

    fig, ax = plt.subplots(figsize=(max(8, len(pivot) * 1.4), 4.5))
    pivot.plot(kind="bar", ax=ax,
               color=[MODEL_COLORS[m] for m in pivot.columns],
               edgecolor="black", linewidth=0.5, width=0.8)

    ax.set_ylabel("Attack Success Rate (%)")
    ax.set_xlabel(group_col.replace("_", " ").title())
    ax.set_title(title)
    ax.legend(title="Model", loc="upper left", framealpha=0.95)
    ax.set_xticklabels([t.get_text().replace("fake_", "").replace("_", " ") for t in ax.get_xticklabels()],
                       rotation=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    out = FIGURES_DIR / filename
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → saved {out.name}")


def report_methodology_agreement(df: pd.DataFrame):
    print("\n=== Methodology validation: deterministic vs Sonnet judge ===")
    df = df.copy()
    df["disagree"] = df["success"] != df["judge_success"]
    by_model = df.groupby("model_label").agg(
        n=("success",         "size"),
        det_successes=("success",         "sum"),
        judge_successes=("judge_success", "sum"),
        disagreements=("disagree",        "sum"),
    ).astype(int).reindex(MODEL_ORDER)
    by_model["agreement_pct"] = ((by_model["n"] - by_model["disagreements"]) / by_model["n"] * 100).round(1)
    print(by_model.to_string())

    overall_agree = (df["success"] == df["judge_success"]).mean() * 100
    print(f"\n  Overall agreement: {overall_agree:.1f}% across {len(df)} rows")


def main():
    df = load_data()

    print(f"Loaded {len(df)} rows from {RESULTS_FILE.relative_to(ROOT)}")
    print(f"  Models:     {sorted(df['model_label'].unique())}")
    print(f"  Carriers:   {sorted(df['carrier_type'].unique())}")
    print(f"  Placements: {sorted(df['placement'].unique())}")

    # ---------- TABLES ----------
    print_table("Overall ASR per model (judge-scored)",
                asr_table(df, ["model_label"]).reindex(MODEL_ORDER))

    print_table("ASR per (model, carrier_type)",
                asr_table(df, ["model_label", "carrier_type"]))

    print_table("ASR per (model, placement)",
                asr_table(df, ["model_label", "placement"]))

    print_table("ASR per (model, attack_type)",
                asr_table(df, ["model_label", "attack_type"]))

    print_table("ASR per (model, payload_source)",
                asr_table(df, ["model_label", "payload_source"]))

    report_methodology_agreement(df)

    # ---------- PLOTS ----------
    print("\n=== Generating plots ===")
    plot_overall_asr(df)
    plot_grouped(df, "carrier_type",   "ASR by Carrier Type",      "02_asr_by_carrier.png")
    plot_grouped(df, "placement",      "ASR by Injection Placement", "03_asr_by_placement.png",
                 order=["visible", "ai_note", "html_comment", "footnote"])
    plot_grouped(df, "attack_type",    "ASR by Attack Type",        "04_asr_by_attack_type.png")
    plot_grouped(df, "payload_source", "ASR by Payload Source",     "05_asr_by_payload_source.png")

    print(f"\nDone. Plots in {FIGURES_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
