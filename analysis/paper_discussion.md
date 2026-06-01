# 6. Discussion and Limitations

## 6.1 Implications

**Vendor choice is a security decision, not just a cost decision.** The 45× gap between Claude Haiku 4.5 and Gemini 2.5 Flash on identical scenarios is large enough that any practitioner deploying an agent that consumes untrusted content must take it seriously. A team that picks a model based purely on cost-per-token or latency benchmarks is implicitly making a security trade-off they may not be aware of. We do not have visibility into *why* the three models differ so sharply — different alignment data, different safety RLHF objectives, different default cautiousness, or some combination — but the result of those differences is that the same attack succeeds in zero, one-quarter, or one-half of cases depending on which vendor's small model is in production.

**The "fake instruction" framing is a generally exploitable vulnerability.** The most successful single tactic in our experiments was wrapping the malicious payload in a fake `===NOTE FOR AI ASSISTANT===` block. The contents of the payload barely mattered; the *framing* of the payload as if it were a system-level instruction more than doubled its success rate on Gemini compared to the same payload sitting visibly at the end of the document. This is an awkward result: model providers have presumably trained models to follow system-style instructions reliably, and the same disposition is being exploited by attackers who can write text that visually resembles a system instruction. A possible mitigation, untested here, would be for models to systematically discount any instruction-formatted text that appears inside user-supplied content. Whether such a defense would generalize without compromising legitimate uses is an open question.

**Markdown footnotes are not a useful attack vector.** Our 0% ASR across all 12 footnote-placement scenarios suggests models reliably recognize footnote markers as structural document conventions and disregard instructions inside them. This is a modest but real positive finding: a hardened markdown rendering convention can hide content from human readers while remaining safe from automated exploitation.

**Scoring methodology is load-bearing for indirect injection benchmarks.** The 1% disagreement between deterministic and judge scoring in our study is small in aggregate but large in implication: it concentrates entirely on the most consequential outcomes (tool-call escalation, partial compliance) that a single-method scorer would mis-classify. Any benchmark in this space should report multi-method scoring and the disagreement rate, not a single number.

## 6.2 Limitations

**Single trial per scenario.** We run each scenario exactly once per model. With `temperature=0`, the same call produces nearly deterministic outputs in practice, but the harness does not estimate within-model variance from re-sampling. We accept this trade-off to keep the cross-model comparison surface area large at fixed budget.

**Cheap-tier models only.** We restricted to small, fast, non-reasoning production models — Claude Haiku 4.5, GPT-4o-mini, Gemini 2.5 Flash. We did not test flagship-tier models (Opus, GPT-5, Gemini Pro) or reasoning models (o-series, GPT-5-reasoning). The susceptibility ranking we report may not generalize to larger or reasoning-equipped models from the same vendors.

**Single-shot only.** Each scenario consists of one API call. Real deployed agents typically operate in multi-turn loops, where a model that initially complies with an injection might "wake up" after seeing the tool's response, or where a model that initially refuses might be drawn in by subsequent context. We measured *first-response default behavior*; we did not measure trajectory-level behavior.

**Single neutral system prompt; no defense conditions.** All models were tested with the same neutral helpful-assistant prompt, with no anti-injection guidance, no untrusted-content tagging, and no spotlighting. A defended-condition rerun was a stretch goal in our project plan but was not completed in scope. The numbers we report are undefended baselines.

**Hand-authored carriers, hand-rewritten payloads.** Both the 5 carrier templates and the 30 rewritten payloads were authored by a single project member. Carrier realism, payload naturalness, and the absence of accidental tells (e.g. distinctive phrasing that a model might learn to flag) are not independently validated. A larger, multi-author corpus would strengthen external validity.

**English-only, US-context documents.** Carriers describe American companies, American resumes, and American meeting structures. Whether the placement findings replicate across other languages and other document conventions is unknown.

**Hand-labeling validation on subset.** Per our project plan, we hand-label a 30-scenario validation subset to compare against the deterministic and judge scoring; this is what calibrates our trust in the auto-scoring. We do not hand-label all 300 trials. The 99% inter-method agreement and the close match to the hand-labeled subset (reported in the validation section) gives us confidence in the headline numbers, but a fully hand-labeled corpus would be a stronger evidence base.

**Mock tools, not live tools.** The harness records tool calls as evidence of intent but does not execute them. This is what makes the experiment safe to run end-to-end at academic scale. But it means the agent never sees a tool's output, never reasons about a tool's failure, and never gets the chance to backtrack from a partially completed action. The "what happens after the tool returns" stage of an attack is unstudied here.

## 6.3 Future work

Natural next steps include (a) running a spotlighting-style defense condition on the same scenarios to measure defense effect size, (b) extending the comparison to flagship-tier and reasoning-equipped models, (c) running multi-turn agent loops to see whether models recover from initial compliance, (d) collecting a larger hand-labeled validation corpus, and (e) varying the system prompt to measure the sensitivity of susceptibility to small prompt changes — the difference, for example, between a generic helpful-assistant prompt and a security-conscious one.

The placement finding in particular suggests a sharper experimental design worth pursuing: rather than treating placement as one of four bucketed strategies, sweep across a continuous space of "how instruction-coded does the surrounding wrapper look" and measure the gradient. We suspect the relationship between visual-instructionality and ASR is steep and monotone, and that finding the inflection point would be useful information for both attackers and defenders to know about.
