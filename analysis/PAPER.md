# Indirect Prompt Injection via Realistic Content Carriers

**A vendor comparison across three cheap production language models.**

CS 410/510 Trustworthy AI · Portland State University · Spring 2026

---

This master document compiles all paper sections into one place for editing and submission. Individual section files (`paper_*.md`) and supplementary materials (`case_studies.md`, `figures/`, `results_analysis.py`) remain in this folder for granular editing.

---

> **§1 Introduction** — see [`paper_intro.md`](paper_intro.md)
>
> **§2 Threat Model** — see [`paper_threat_model.md`](paper_threat_model.md)
>
> **§3 Related Work** — see [`paper_related_work.md`](paper_related_work.md)
>
> **§4 Method** — see [`paper_method.md`](paper_method.md)
>
> **§5 Results** — see [`paper_results.md`](paper_results.md)
>
> **§6 Discussion and Limitations** — see [`paper_discussion.md`](paper_discussion.md)
>
> **Supplementary — Case Studies** — see [`case_studies.md`](case_studies.md)
>
> **Supplementary — Figures** — see [`figures/`](figures/)

---

## How to assemble the final paper

For a single-document submission, concatenate in this order:

```bash
cat paper_intro.md paper_threat_model.md paper_related_work.md \
    paper_method.md paper_results.md paper_discussion.md \
    > FINAL_PAPER.md
```

Then for PDF, run through pandoc:

```bash
pandoc FINAL_PAPER.md -o FINAL_PAPER.pdf \
    --pdf-engine=xelatex --variable=geometry:margin=1in
```

Insert PNG figures from `figures/` at the marked `*[FIGURE: ...]*` placeholders in `paper_results.md`.

---

## Headline numbers for quick reference

| Model | Successes | ASR | Notes |
|---|---|---|---|
| Claude Haiku 4.5 | 1 / 100 | **1.0%** | The 1 success was a "mild URL inclusion" injection in meeting notes |
| GPT-4o-mini | 27 / 100 | **27.0%** | Includes 1 case where tool was called instead of text-substring (sc_071) |
| Gemini 2.5 Flash | 45 / 100 | **45.0%** | Highest susceptibility; nearly uniform across carrier types |

**Headline placement effect on the most susceptible model (Gemini):**
- `ai_note` (fake "===NOTE FOR AI ASSISTANT===" wrapper): **82.6%** ASR
- `visible` (plain text at bottom): 37.9% ASR
- `html_comment` (inside HTML comment): 26.7% ASR
- `footnote` (markdown footnote): **0.0%** ASR

**Methodological validation:** 99.0% agreement between deterministic substring/tool-call scoring and Sonnet 4.6 universal judge across all 300 trials. 3 disagreements; each one a meaningful edge case the deterministic scorer was structurally designed to miss.

---

## Repository pointers

- `harness/` — runners, scorer, eval scripts, judge pass, combine script
- `scenarios/scenarios.json` — the canonical 100 scenarios
- `payloads/payloads.json` — 30 source payloads with metadata
- `carriers/` — 15 carrier templates (5 types × 3 placements)
- `results/results.csv` — 300-row combined results with deterministic and judge scores
- `analysis/figures/` — 5 generated PNG plots
- `analysis/` — this folder, all paper sections and the analysis script
