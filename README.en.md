# xhs-content

A Codex / OpenClaw skill for Xiaohongshu (XHS) image-note creation. One `post-package.json` holds the title, complete caption, hashtags, cover, and publish payload so the reviewed draft and the published version stay identical.

**English** | [中文](./README.md)

## What It Does

| Capability | Output |
| --- | --- |
| Topic research | XHS search results, recurring hooks, comment questions, and differentiated angles |
| Image-note creation | A complete Chinese XHS caption, hashtags, and one 3:4 cover |
| Cover research | A private same-topic reference wall for analysis, never for reuse |
| Scene-led covers | A per-post subject, composition, text-safe area, and text-free scene-image prompt |
| Carousels | 2–10 slides for lists, steps, and comparisons |
| Final publishing | A locked title, full caption, hashtags, and cover uploaded as one image note |

## Workflow

1. **Research the category first.** For a new cover, collect and inspect current high-engagement XHS notes for the exact topic. Extract conventions; never use the reference covers as final assets.
2. **Create one complete post package.** The caption, hashtags, cover copy, and visual direction live in `post-package.json`.
3. **Choose the cover treatment from the content.** Pets, venues, products, travel, and personal stories use subject-relevant scenes. Career opinions and comparisons may use a text-led editorial cover when the research supports it. New covers are not selected from a fixed template library.
4. **Publish only after approval.** The final title, full caption, hashtags, and cover are locked together. Any change invalidates the lock.

## Important Limits

- A complete post defaults to a **full caption plus one cover**. Text-only output requires an explicit request.
- The cover must visibly belong to the topic: kitten posts show a kitten, venue posts show the venue or food, and product posts show the product.
- Photo-led covers need a new, text-free background image. `xhs-scene-prompt.py` exports the unique image brief; it **does not generate the bitmap itself**. Use an available image-generation tool or a properly licensed image source for that background.
- Third-party reference covers are local analysis material only. Never publish them, use them as final backgrounds, or commit them.
- Verify high-stakes factual claims such as admissions, policy, medicine, salaries, and employment. Publishing is an external action and requires explicit final approval.

## Install

### Codex

```bash
git clone https://github.com/ffffff9331/xhs-content.git ~/.codex/skills/xhs-content
```

Refresh Codex, then ask for a post in chat.

### OpenClaw

For OpenClaw environments with Git-based skill installation:

```bash
openclaw skills install git:ffffff9331/xhs-content@main
```

## Usage

The examples below use “weekend city cycling” as one continuous topic. Replace it with your own subject.

### 1. Create one image note

```text
Use xhs-content to create an XHS post: “My first weekend city ride: how do I plan the route, food, and outfit without a mess?”
I need the full caption and one cover. Both must feel distinctly Xiaohongshu-native.
```

Default output:

```text
data/<date>-<keyword>/
├── post-package.json
├── cover-research/
└── publish/
    ├── cover.svg
    └── cover.png
```

### 2. Research, then create

```text
Research current Xiaohongshu posts about weekend city cycling and give me a trend report.
Then choose one differentiated angle and turn it into a full caption and one cover.
```

Research also creates `sources.jsonl`, `report.md`, and a private `cover-research/` directory. Images inside the cover-research directory must not be published or committed.

### 3. Build a carousel

```text
Turn “My first weekend city ride: 5 things not to miss before leaving” into a six-slide Xiaohongshu carousel.
```

Carousels suit steps, checklists, and comparisons. Their first slide follows the same cover-research and style rules.

## Photo-Led Covers

For a scene-led cover, first write the literal subject, setting, camera treatment, text-safe area, and avoid list in `post-package.json`. Export the unique prompt:

```bash
python3 scripts/xhs-scene-prompt.py \
  --input data/<date>-<keyword>/post-package.json \
  --json
```

Generate or obtain one **text-free, watermark-free, 3:4** scene image, save it as `publish/background.png`, then render the Chinese cover typography:

```bash
python3 scripts/xhs-cover.py \
  --input data/<date>-<keyword>/post-package.json \
  --background data/<date>-<keyword>/publish/background.png \
  --out-dir data/<date>-<keyword>/publish
```

When research supports a text-led opinion cover, the visual blueprint may explicitly disable the background image. Do not force every category into the same photo treatment or layout.

## Publish an Approved Version

Run these commands only after the user approves the exact title, full caption, hashtags, cover, visibility, and timing:

```bash
python3 scripts/xhs-style-check.py \
  --input data/<date>-<keyword>/post-package.json \
  --cover data/<date>-<keyword>/publish/cover.png \
  --strict --require-visual --require-cover-research --write-lock

python3 scripts/xhs-publish.py \
  --input data/<date>-<keyword>/post-package.json \
  --cover data/<date>-<keyword>/publish/cover.png \
  --publish
```

The publisher uses the current creator-page `上传图文` entry. It proceeds only when the lock exactly matches the title, full caption, hashtags, and cover. It stops for login, CAPTCHA, declarations, or unexpected dialogs.

## Requirements

- Python 3.8+
- An available Chinese font
- [`xhs-cli`](https://github.com/jackwener/xhs-cli) for XHS search, login, and publishing
- Pillow (optional, for the local reference wall)
- Optional image-generation capability or properly licensed text-free scene images

Before first XHS research or publishing, log in locally:

```bash
xhs login
```

Never commit cookies, QR codes, login information, unapproved drafts, test output, or third-party images from `cover-research/`.

## Core Files

| File | Purpose |
| --- | --- |
| `SKILL.md` | Execution rules for the skill |
| `references/post-package.md` | `post-package.json` field reference |
| `scripts/xhs-search.py` | Topic search |
| `scripts/xhs-cover-research.py` | Same-topic cover research |
| `scripts/xhs-scene-prompt.py` | Per-post scene-image prompt |
| `scripts/xhs-cover.py` | Chinese cover rendering |
| `scripts/xhs-carousel.py` | Carousel rendering |
| `scripts/xhs-style-check.py` | Style validation and final-version locking |
| `scripts/xhs-publish.py` | Locked image-note publishing |

## License

[MIT](./LICENSE)
