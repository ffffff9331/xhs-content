# xhs-content

A Codex / OpenClaw skill for creating complete Xiaohongshu (XHS) posts: research a topic, write a distinctly XHS-native caption, render a scroll-stopping cover, lock the approved version, and publish the final image note.

This is not a generic article generator with an unrelated poster. Every complete post uses one `post-package.json` as the source of truth for its title, full caption, hashtags, cover, and publish payload.

**English** | [中文](./README.md)

## What It Does

| Capability | Result |
| --- | --- |
| Topic research | Collects XHS notes and produces trend signals, recurring hooks, comment questions, differentiated angles, and a source table |
| XHS-native captions | Opens with a hook, uses phone-readable paragraphs and conversational Chinese, gives a usable point of view, and ends with a comment prompt |
| One strong cover | Produces a 3:4 vertical cover with big headline lines, a high-contrast hook, context badge, and a phone-readable hierarchy |
| Scene-image support | Can use a text-free AI-generated scene as the cover background, then apply deterministic Chinese typography |
| Carousels | Creates 2–10 slide carousels for lists, steps, and explainers |
| Final-version lock | Hashes the title, full caption including hashtags, and cover to prevent an accidental short preview from being published |
| XHS publishing | Targets the current creator-page upload tab and publish control, and only publishes the locked final package |

## Non-Negotiable Creative Rules

- **The caption must look and feel like Xiaohongshu.** The hook lands in the first 1–3 lines; the tone is conversational, paragraphs are short, advice is concrete, and the close asks for a specific comment.
- **The cover must look and feel like Xiaohongshu.** It is a 3:4 vertical image with 2–3 large headline lines, a high-contrast hook, a small context badge, and confident hierarchy. The default coral, ink, and warm-white palette avoids muted slideshow aesthetics.
- **A complete post defaults to one cover plus the full caption.** Text-only is produced only when the user explicitly requests it.
- **Approved long copy is immutable.** A short version is allowed only when explicitly requested and packaged separately with `mode: "short"`.
- **Only a locked package can publish.** Any title, full-caption, hashtag, or cover change invalidates the lock and requires approval again.

## Install

### Codex

Clone this repository into the Codex skills directory:

```bash
git clone https://github.com/ffffff9331/xhs-content.git ~/.codex/skills/xhs-content
```

After restarting or refreshing Codex, ask for a complete post:

```text
Use xhs-content to create an XHS post about nursing graduate-school admissions, with the full caption and one bold cover.
```

### OpenClaw

For an OpenClaw environment that supports Git-based skill installation:

```bash
openclaw skills install git:ffffff9331/xhs-content@main
```

## Typical Workflows

### Research, Then Create

```text
Research current Xiaohongshu conversations about nursing graduate school, then create a post titled “After a nursing master's, you still work in a hospital. What did three years really buy you?” with one cover.
```

Research output is stored under:

```text
data/<date>-<keyword>/
├── sources.jsonl
├── report.md
├── drafts.md
└── post-package.json
```

For claims involving admissions, fees, policy, medical information, salaries, or employment, verify official sources before presenting them as fact.

### Create One Image Note

```text
Create an XHS post: How should people from second-tier universities, repeat test takers, working professionals, and people over 30 assess the risk and pace of graduate-school entrance exams? Make the caption and the one cover unmistakably Xiaohongshu-style.
```

The default deliverables are:

- Title
- Full caption and hashtags
- `post-package.json`
- `publish/cover.png`

### Use An AI Scene Image As A Cover Background

```text
Generate a text-free study-room scene for nursing graduate-school preparation, then use it as the background of an XHS cover.
```

Scene images must contain **no embedded text or Chinese characters**. The cover renderer is responsible for Chinese headline typography, preventing garbled text and inconsistent fonts.

### Build A Carousel

```text
Turn “The nursing master's ledger: tuition, stipends, opportunity cost, and the returns you cannot quantify” into a 6-slide XHS carousel.
```

### Publish The Approved Final Version

Only after the user explicitly approves the exact title, **full caption**, hashtags, cover, visibility, and timing:

```bash
python3 scripts/xhs-style-check.py \
  --input data/<date>-<keyword>/post-package.json \
  --cover data/<date>-<keyword>/publish/cover.png \
  --strict --write-lock

python3 scripts/xhs-publish.py \
  --input data/<date>-<keyword>/post-package.json \
  --cover data/<date>-<keyword>/publish/cover.png \
  --publish
```

The publisher switches to the current creator page’s image-note upload tab and uses the current publish control. It refuses any payload that does not exactly match the approved lock.

## Core Files

| File | Purpose |
| --- | --- |
| `scripts/xhs-search.py` | Collect XHS notes for a keyword |
| `scripts/xhs-cover.py` | Render one 3:4, Chinese-typography-safe, bold XHS cover |
| `scripts/xhs-carousel.py` | Render a multi-slide carousel |
| `scripts/xhs-style-check.py` | Validate XHS style and final-version locks |
| `scripts/xhs-publish.py` | Publish a locked image-note package |
| `references/post-package.md` | Schema for the single-source-of-truth post package |
| `references/style-qa.md` | Editorial and visual QA checklist |

## Dependencies And Login

### Research

Research uses [`xhs-cli`](https://github.com/jackwener/xhs-cli):

```bash
pipx install xhs-cli
xhs login
```

Initial login is completed locally. Cookies are managed by `xhs-cli` and must never be committed, shared, or included in generated packages.

### Covers And Images

- Python 3.8+
- An available Chinese font
- Optional image-generation capability for text-free scene backgrounds

Without an image generator, `xhs-cover.py` still produces a usable information-card cover.

## Repository Layout

```text
xhs-content/
├── SKILL.md
├── README.md
├── README.en.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── prompt.md
│   ├── post-package.md
│   ├── style-qa.md
│   └── carousel.md
└── scripts/
    ├── xhs-search.py
    ├── xhs-cover.py
    ├── xhs-carousel.py
    ├── xhs-style-check.py
    └── xhs-publish.py
```

## Notes

- XHS page structure and anti-bot measures can change. Re-run `xhs login` when research authentication expires.
- Publishing is an external action and requires explicit user approval of the final version.
- Never commit QR codes, cookies, creator-page login data, unapproved drafts, or test output.

## License

[MIT](./LICENSE)
