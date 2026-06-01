# 3. Related Work

Our study sits at the intersection of two active threads in the AI safety literature: red-teaming benchmarks for harmful agent behavior, and the emerging body of work on indirect prompt injection specifically.

## 3.1 Direct red-teaming benchmarks

**AdvBench** (Zou et al., 2023, *Universal and Transferable Adversarial Attacks on Aligned Language Models*) provides a corpus of harmful behavior prompts — direct user-to-model requests for harmful content or actions — paired with the GCG attack technique for eliciting compliance from aligned models. AdvBench has become a foundational reference for jailbreak research and supplies 15 of our 30 payloads after rewriting.

**AgentHarm** (Andriushchenko et al., UK AI Safety Institute) extends red-teaming from text-generation models to *agents* — models with tool access. AgentHarm scenarios describe actions a deployed agent might be asked to take (transfer money, send phishing email, exfiltrate data, etc.), grouped by harm category. It supplies the other 15 of our 30 payloads. AgentHarm is designed for the direct-attack setting (the user asks the agent to perform the harmful action); we adapt the payloads for indirect attack by rephrasing each as third-party document content.

Both benchmarks measure *whether a model will comply with a directly stated harmful request*. They do not, on their own, measure whether a model will comply with the *same intent* arriving via an indirect channel.

## 3.2 Indirect prompt injection

**Greshake et al. (2023)**, *Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*, is the foundational work introducing indirect prompt injection as a distinct threat class. They demonstrate concrete attacks against deployed systems including Microsoft Bing Chat and ChatGPT plugins, showing that injected instructions in retrieved web content can hijack the assistant. Our study extends this work by moving from existence proofs against specific systems to a controlled factorial measurement across multiple models and multiple placement strategies.

**InjecAgent** (Zhan et al., 2024), *Benchmarking Indirect Prompt Injection of Tool-Integrated LLM Agents*, builds an automated benchmark for indirect injection against tool-using agents. InjecAgent uses synthetically generated injection strings in a synthetic agent-environment harness. Our study differs in two ways: first, we use *realistic* carrier documents (hand-authored 300-500 word documents written in domain-typical voice) rather than synthetic environment text; second, we explicitly vary the *placement* of the injection inside the carrier as an independent variable, isolating the contribution of presentation form from the contribution of payload content.

**Spotlighting** (Hines et al., 2024, Microsoft), *Defending Against Indirect Prompt Injection Attacks With Spotlighting*, proposes a class of defenses that mark untrusted content with explicit tags or transformations (e.g. wrapping in `[UNTRUSTED]…[/UNTRUSTED]`) and instruct the model to treat tagged content as data rather than instructions. We do not evaluate spotlighting in this study; we deliberately use a neutral system prompt to measure undefended baseline susceptibility, and leave a defended-versus-undefended comparison to future work.

## 3.3 Positioning of this work

Compared to the above, this paper contributes:

1. **A vendor-comparison across three cheap production models** under identical conditions. Prior work tends to test one or two models, often at the flagship tier; our comparison across three vendors at the cheap/fast tier informs the deployment-time decision practitioners actually face.

2. **A controlled placement × carrier × attack-type factorial design**, isolating where in the document a payload lives, what kind of document it lives in, and what action it is trying to elicit. The placement finding — that fake instruction-coded blocks (`===NOTE FOR AI ASSISTANT===`) substantially outperform plain visible text — has not, to our knowledge, been quantified at this granularity in prior work.

3. **A dual-scoring methodology** combining deterministic rules with a universal LLM judge, with explicit treatment of failure modes (tool-call escalation, partial compliance, false-positive substring matches) that single-method scoring would conflate.
