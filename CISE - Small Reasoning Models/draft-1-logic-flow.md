# Proposal Logic Flow: Self-Training Small Reasoning Models

Source PDF: `draft-1.pdf`

```mermaid
flowchart LR
  A["Motivation / Gap<br/>Agentic AI relies on large LLM/MLLM backends<br/>Scaling and customization are costly<br/>Open models lag closed reasoning systems"] --> B["Central Thesis<br/>Use distillation to build small reasoning models<br/>Preserve capabilities while reducing compute<br/>Use transfer analysis for interpretable design rules"]

  B --> C1["Aim 1: Intra-Family Distillation<br/>Weight initialization<br/>Student-teacher alignment<br/>Post-distillation fine-tuning"]
  C1 --> C2["Aim 2: Multimodal LLM Distillation<br/>Extend to visual and multimodal reasoning"]
  C1 --> C3["Aim 3: Data-Constrained Multitask Distillation<br/>Template mixing<br/>Few-shot distillation<br/>Sample selection and augmentation"]
  C1 --> C4["Aim 4: Cross-Family and Architecture-Agnostic Distillation<br/>Tokenizer, vocabulary, policy, hidden-state, and architecture mismatch<br/>Projection and semantic-alignment objectives"]

  C2 --> D["Shared Evaluation Methodology"]
  C3 --> D
  C4 --> D

  D --> D1["Baselines<br/>SFT, standard KD, SeqKD, RKL, JD, JSD, AKL, on-policy and off-policy methods"]
  D --> D2["Datasets<br/>DollyEval, SelfInst, VicunaEval, S-NI, UnNI"]
  D --> D3["Metrics<br/>Rouge-L, GPT-4o-mini judge, SBERT"]
  D --> E["Agentic Integration<br/>SWE-bench, OSWorld, BrowserGym"]

  E --> C1
  E --> F["Outcomes<br/>Efficient reasoning models<br/>Responsible open-source code and weights<br/>Edge/local assistants and VLA-style systems<br/>Graduate, undergraduate, and workforce training"]
```

## Reading Of The Proposal Logic

The proposal starts from the practical constraint that modern agents depend on large model backends that are expensive to train, modify, and deploy. The central response is to study distillation as a way to transfer reasoning ability into smaller models while also learning which mechanisms make that transfer work.

The research plan builds outward from a controlled case. Aim 1 studies intra-family distillation where teacher and student are closely related. Later aims relax that assumption: first to multimodal models, then to multitask settings with uneven data, then to cross-family and architecture-agnostic transfer where tokenizers, vocabularies, policies, and representations may not align.

The evaluation plan is shared across the aims and closes the loop. Standard language-generation benchmarks and metrics test model quality, while agentic benchmarks test whether the distilled models actually work inside harnesses. Failures from those agent evaluations are meant to feed the next iteration of distillation method design.
