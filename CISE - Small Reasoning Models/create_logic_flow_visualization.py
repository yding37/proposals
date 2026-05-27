from pathlib import Path
import textwrap
from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
PNG_OUT = BASE / "draft-1-logic-flow.png"
MD_OUT = BASE / "draft-1-logic-flow.md"

W, H = 2500, 1650
MARGIN = 90
TITLE_H = 165
BG = "#f7f5ef"
INK = "#1f2933"
MUTED = "#52616b"
GRID = "#d7d1c5"

COLORS = {
    "motivation": ("#fff7e6", "#d98b00"),
    "thesis": ("#ecf8f2", "#178c5f"),
    "aims": ("#eef4ff", "#3366cc"),
    "eval": ("#fff0f0", "#cc4b4b"),
    "outcomes": ("#f4efff", "#7a4cc2"),
}


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


F_TITLE = font(54, True)
F_SUBTITLE = font(28)
F_STAGE = font(31, True)
F_CARD_TITLE = font(27, True)
F_BODY = font(24)
F_SMALL = font(20)


def rounded(draw, box, radius, fill, outline, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_to_width(draw, text, font_obj, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=font_obj)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_text_block(draw, x, y, w, title, bullets, accent, fill, max_bullets=None):
    title_lines = wrap_to_width(draw, title, F_CARD_TITLE, w - 42)
    body_lines = []
    shown = bullets if max_bullets is None else bullets[:max_bullets]
    for bullet in shown:
        wrapped = wrap_to_width(draw, bullet, F_BODY, w - 78)
        body_lines.append(wrapped)
    title_h = len(title_lines) * 34
    body_h = sum(len(lines) * 30 + 8 for lines in body_lines)
    h = 36 + title_h + 16 + body_h + 20
    rounded(draw, (x, y, x + w, y + h), 18, fill, accent, 3)
    draw.rectangle((x, y, x + 14, y + h), fill=accent)

    ty = y + 24
    for line in title_lines:
        draw.text((x + 30, ty), line, font=F_CARD_TITLE, fill=INK)
        ty += 34
    ty += 8
    for lines in body_lines:
        draw.ellipse((x + 32, ty + 9, x + 42, ty + 19), fill=accent)
        ly = ty
        for line in lines:
            draw.text((x + 55, ly), line, font=F_BODY, fill=INK)
            ly += 30
        ty = ly + 8
    return h


def arrow(draw, start, end, color="#59636e", width=5):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    if x2 >= x1:
        pts = [(x2, y2), (x2 - 22, y2 - 12), (x2 - 22, y2 + 12)]
    else:
        pts = [(x2, y2), (x2 + 22, y2 - 12), (x2 + 22, y2 + 12)]
    draw.polygon(pts, fill=color)


def draw_stage(draw, x, y, w, h, label, key):
    fill, accent = COLORS[key]
    rounded(draw, (x, y, x + w, y + h), 24, "#ffffff", GRID, 3)
    draw.rounded_rectangle((x, y, x + w, y + 72), radius=24, fill=fill, outline=GRID, width=0)
    draw.rectangle((x, y + 48, x + w, y + 72), fill=fill)
    draw.text((x + 28, y + 21), label, font=F_STAGE, fill=accent)
    return fill, accent


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((MARGIN, 45), "Self-Training Small Reasoning Models", font=F_TITLE, fill=INK)
    draw.text(
        (MARGIN, 112),
        "Proposal logic flow extracted from draft-1.pdf: motivation -> research engine -> evaluation -> outcomes",
        font=F_SUBTITLE,
        fill=MUTED,
    )

    stage_y = TITLE_H + 35
    stage_h = H - stage_y - 95
    gap = 30
    widths = [390, 390, 630, 455, 365]
    xs = [MARGIN]
    for w in widths[:-1]:
        xs.append(xs[-1] + w + gap)

    stages = [
        ("1. Motivation / Gap", "motivation"),
        ("2. Central Thesis", "thesis"),
        ("3. Research Aims", "aims"),
        ("4. Evaluation Loop", "eval"),
        ("5. Outcomes", "outcomes"),
    ]
    fills = {}
    accents = {}
    for x, w, (label, key) in zip(xs, widths, stages):
        fill, accent = draw_stage(draw, x, stage_y, w, stage_h, label, key)
        fills[key] = fill
        accents[key] = accent

    content_y = stage_y + 100

    draw_text_block(
        draw,
        xs[0] + 24,
        content_y,
        widths[0] - 48,
        "Why the project is needed",
        [
            "Agentic AI depends on large LLM and MLLM backends.",
            "Scaling and customization are expensive; reasoning gains may plateau.",
            "Open models lag closed systems on key reasoning benchmarks.",
            "Resource-constrained settings need efficient adaptable models.",
        ],
        accents["motivation"],
        fills["motivation"],
    )

    draw_text_block(
        draw,
        xs[1] + 24,
        content_y,
        widths[1] - 48,
        "Core hypothesis",
        [
            "Distillation can transfer advanced reasoning into smaller specialized models.",
            "Small models can retain useful capabilities while reducing compute cost.",
            "Studying transfer mechanisms yields interpretable design rules.",
        ],
        accents["thesis"],
        fills["thesis"],
    )

    aim_x = xs[2] + 24
    aim_w = widths[2] - 48
    aim_y = content_y
    aim_cards = [
        (
            "Aim 1: Efficient intra-family distillation",
            [
                "Teacher and student from the same family.",
                "Study weight initialization, output and hidden-state alignment, and post-distillation tuning.",
            ],
        ),
        (
            "Aim 2: Multimodal LLM distillation",
            [
                "Extend the distillation framework to visual and multimodal reasoning models.",
                "Connect efficient representation learning to multimodal understanding.",
            ],
        ),
        (
            "Aim 3: Multitask distillation under data constraints",
            [
                "Preserve capabilities across tasks when data availability is uneven.",
                "Investigate template mixing, few-shot distillation, sample selection, augmentation, and custom objectives.",
            ],
        ),
        (
            "Aim 4: Cross-family and architecture-agnostic distillation",
            [
                "Handle tokenizer, vocabulary, policy, hidden-state, and architecture mismatch.",
                "Learn projections and objectives that reduce semantic mismatch across model families.",
            ],
        ),
    ]
    for title, bullets in aim_cards:
        h = draw_text_block(draw, aim_x, aim_y, aim_w, title, bullets, accents["aims"], fills["aims"])
        aim_y += h + 22

    eval_y = content_y
    eval_cards = [
        (
            "Baselines",
            ["SFT, standard KD, SeqKD, RKL, JD, JSD, AKL, plus on-policy and off-policy distillation."],
        ),
        (
            "Datasets",
            ["DollyEval, SelfInst, VicunaEval, S-NI, and UnNI for instruction following and long-form generation."],
        ),
        (
            "Metrics and judges",
            ["Rouge-L, GPT-4o-mini semantic judgments, and SBERT similarity."],
        ),
        (
            "Agentic integration",
            ["SWE-bench, OSWorld, and BrowserGym test whether distilled models work inside real agent harnesses."],
        ),
    ]
    for title, bullets in eval_cards:
        h = draw_text_block(
            draw,
            xs[3] + 24,
            eval_y,
            widths[3] - 48,
            title,
            bullets,
            accents["eval"],
            fills["eval"],
        )
        eval_y += h + 28

    draw_text_block(
        draw,
        xs[4] + 24,
        content_y,
        widths[4] - 48,
        "Scientific outputs",
        [
            "New distillation methods and design principles.",
            "Open-source code and weights under responsible AI practices.",
            "Efficient models for edge, local assistants, and VLA-style systems.",
        ],
        accents["outcomes"],
        fills["outcomes"],
    )
    draw_text_block(
        draw,
        xs[4] + 24,
        content_y + 520,
        widths[4] - 48,
        "Broader impacts",
        [
            "Train two PhD students and involve undergraduate researchers.",
            "Bring generative AI and multimodal ML into curriculum and workforce training.",
            "Reduce compute and energy barriers to AI deployment.",
        ],
        accents["outcomes"],
        fills["outcomes"],
    )

    mid_y = stage_y + stage_h / 2
    for i in range(4):
        arrow(draw, (xs[i] + widths[i] + 4, mid_y), (xs[i + 1] - 4, mid_y), width=6)

    # Feedback arc from agent/evaluation back to the research aims.
    y_arc = stage_y + stage_h - 76
    draw.line((xs[3] + widths[3] * 0.55, y_arc, xs[3] + widths[3] * 0.55, y_arc + 34), fill=accents["eval"], width=5)
    draw.line((xs[3] + widths[3] * 0.55, y_arc + 34, xs[2] + widths[2] * 0.5, y_arc + 34), fill=accents["eval"], width=5)
    arrow(draw, (xs[2] + widths[2] * 0.5, y_arc + 34), (xs[2] + widths[2] * 0.5, y_arc), color=accents["eval"], width=5)
    draw.text((xs[2] + 80, y_arc + 43), "Benchmark failures feed the next distillation iteration", font=F_SMALL, fill=accents["eval"])

    draw.text(
        (MARGIN, H - 55),
        "Source: draft-1.pdf, extracted with pypdf. Diagram is an interpretation of the proposal structure, not a verbatim page.",
        font=F_SMALL,
        fill=MUTED,
    )

    img.save(PNG_OUT)

    mermaid = """# Proposal Logic Flow: Self-Training Small Reasoning Models

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
"""
    MD_OUT.write_text(mermaid, encoding="utf-8")
    print(PNG_OUT)
    print(MD_OUT)


if __name__ == "__main__":
    main()
