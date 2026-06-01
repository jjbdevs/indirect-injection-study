# 2. Threat Model

We study an attacker whose goal is to redirect the behavior of an LLM-based agent acting on a benign user's behalf, by planting a malicious instruction inside content the agent will consume while completing the user's task.

## 2.1 Attacker

The attacker controls the *content of a document* that the user will ask an agent to process — a webpage, an email, a resume, a meeting note, a wiki entry, a product page. The attacker does not have direct access to the model, the agent, the API, or the user's session. They cannot inject text into the system prompt, the user's message, or the agent's tool outputs. Their only channel is the carrier document itself.

The attacker's capability is realistic and broad. They might:

- Own a website the agent might browse.
- Sell a product on a marketplace whose listings the agent might summarize.
- Post a resume to a hiring platform an agent might evaluate.
- Send an email an agent might triage.
- Edit a wiki page or a public document the agent might cite.

In each case, the attacker has full editorial control over the carrier document and can craft injection content with arbitrary care and arbitrary structure (visible text, HTML comments, fake instruction-coded blocks, markdown footnotes, etc.).

## 2.2 Defender

The defender is the user delegating a benign task to an LLM-based agent — for example, asking the agent to summarize an article, evaluate a candidate, or extract key takeaways from a meeting. The user's intent is legitimate and unrelated to the attacker's goal. The user does not read every byte of the source document before delegating the task; the whole point of using an agent is to avoid that.

The deployed agent has access to a set of tools — email, file management, URL fetching, social media posting, contact list access — chosen by the application developer based on the agent's intended use. The agent is configured with a neutral helpful-assistant system prompt; it has not been hardened with explicit anti-injection instructions, content-tagging conventions, or sandboxing of untrusted input.

## 2.3 Attack goals

We measure two classes of attack outcome:

**Tool call attacks:** The attacker wants the agent to take an action on the user's behalf — send a phishing email to the user's contacts, transfer funds, delete files, fetch a malicious URL, post defamatory content. Success is measured by whether the agent invoked the targeted tool with the attacker-controlled content.

**Output manipulation attacks:** The attacker wants the agent's response (which the user will read) to contain attacker-chosen content — a malicious URL the user might click, false information about a product, propaganda, dox of a third party. Success is measured by whether the attacker's content appears in the agent's output.

Both outcomes constitute real harm. A tool-call attack converts the agent into a participant in the attack chain. An output-manipulation attack converts the agent into a delivery mechanism for content the user did not request and would not trust if surfaced by a less authoritative channel.

## 2.4 What makes this realistic

Three properties of our scenarios are intended to reflect real-world deployment conditions:

1. **The user task is benign and reasonable.** "Summarize this article" is the kind of task an agent receives constantly; nothing about the user's request suggests the agent should be on alert.

2. **The carrier documents are plausible.** They are not adversarial benchmark prompts in a bare-text format; they are 300-500 word documents written in domain-typical voice (news article, resume, wiki entry, etc.) with the malicious payload occupying only a small fraction of the total text.

3. **The injection payloads are realistic rephrasings of harmful intents** drawn from published benchmarks (AgentHarm, AdvBench), rewritten to read as content a third party might naturally include in such a document (e.g. a "TECHNICAL NOTE" or an editorial footnote). The harm catalog is grounded in the same red-teaming work the AI safety community has already produced for direct attacks.

## 2.5 What is out of scope

We do not study:

- **Direct prompt injection** (the user is the attacker).
- **Model jailbreaks** (forcing the model to produce harmful content unrelated to a benign task).
- **Multi-turn agent attacks** that exploit feedback loops between the model and its environment over many turns.
- **Defense mechanisms.** A baseline-versus-defended comparison (e.g. with the spotlighting technique) is left as future work; here we are measuring undefended susceptibility.
- **Reasoning-model targets.** We restrict to small, fast, non-reasoning production models because those are what gets shipped at scale and because reasoning models introduce confounding variables (extended-thinking tokens, variable per-trial cost, deliberate inference-time chain-of-thought).
