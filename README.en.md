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
| Category cover research | Before every cover, collects current high-engagement same-topic covers into a private reference sheet, then analyzes composition, text density, color, and subject treatment |
| Content-aware covers | Defines the literal subject, mood, required visual elements, and text-safe area first. A kitten post must show a kitten; a product post must show the product |
| Scene-image support | Derives a unique text-free scene prompt for every photo-led post, creates a subject-relevant new AI-generated or rights-cleared background, then applies deterministic Chinese typography |
| Carousels | Creates 2–10 slide carousels for lists, steps, and explainers |
| Final-version lock | Hashes the title, full caption including hashtags, and cover to prevent an accidental short preview from being published |
| XHS publishing | Targets the current creator-page upload tab and publish control, and only publishes the locked final package |

## Non-Negotiable Creative Rules

- **The caption must look and feel like Xiaohongshu.** The hook lands in the first 1–3 lines; the tone is conversational, paragraphs are short, advice is concrete, and the close asks for a specific comment.
- **The cover must look and feel like Xiaohongshu.** It is a 3:4 vertical image with a scroll-stopping subject and phone-readable hierarchy. A raw food or lifestyle cover may need only one or two large lines over the scene, while a comparison may earn a badge and high-contrast hook. Each category chooses its own researched contrast palette rather than forcing every topic into one color system.
- **Every cover begins with same-category research.** The skill searches current high-engagement XHS notes for the exact topic, creates a private reference sheet, and inspects composition, title density, color, subject scale, and badge placement. The final cover may use category-level conventions only: it must have a new scene, copy, and composition, never reuse a reference image, headline, or recognisable creator treatment.
- **New covers do not select from a fixed template library.** Each one requires a `cover.design` visual blueprint that directly specifies this post's image crop, text zones, overlays, emphasis elements, and footer. Legacy layouts remain only for backwards compatibility.
- **The cover must belong to this exact note.** New posts define `cover.visual` first. Use `photo-story` for a literal subject-led scene, `photo-diary` for lifestyle/personal memory, `product-focus` for products, venues, food, objects, or destinations, `editorial` for careers, education, interviews, or a strong point of view, and `checklist` only for genuine lists, comparisons, or processes. Different industries must not inherit the same unrelated template.
- **Every photo-led cover receives a genuinely new background.** `cover.scene` records this note's shot, setting, action, literal subject, lighting, and text-safe area, plus a negative prompt for text, Chinese characters, logos, watermarks, and category-specific mistakes. It becomes the exact input for image generation. Pets, restaurants, careers, and nursing cannot be the same image with different copy or colors.
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
Use xhs-content to create an XHS post titled “How I cleared 10 square meters in a 20-square-meter rental bedroom,” with the full caption and one bold cover.
```

### OpenClaw

For an OpenClaw environment that supports Git-based skill installation:

```bash
openclaw skills install git:ffffff9331/xhs-content@main
```

## Typical Workflows

### Research, Then Create

```text
Research current Xiaohongshu conversations about weekend camping, then create a post titled “Your first camping trip with a dog: don't turn the weekend into a disaster scene” with one cover.
```

Research output is stored under:

```text
data/<date>-<keyword>/
├── sources.jsonl
├── report.md
├── drafts.md
├── cover-research/
│   ├── cover-references.json
│   ├── cover-reference-wall.html
│   ├── cover-reference-sheet.jpg
│   └── reference-covers/
└── post-package.json
```

For claims involving admissions, fees, policy, medical information, salaries, or employment, verify official sources before presenting them as fact.

### Create One Image Note

```text
Create an XHS post: In your third working year, should you resign before looking, job-hunt while employed, or save six months of expenses first? Make the caption and the one cover unmistakably Xiaohongshu-style.
```

The default deliverables are:

- Title
- Full caption and hashtags
- `post-package.json`
- `publish/cover.png`

Before `publish/cover.png` is rendered, the skill also runs same-category cover research. For example, a first camping trip with a dog searches both `带狗露营` and `宠物露营装备`, inspects the current high-engagement visual conventions, then chooses an original photo-diary, product-focus, or checklist treatment. Research references stay in the local `cover-research/` folder and must never be published, used as final-cover backgrounds, or committed.

The resulting cover is not mechanically assigned a template name. The skill creates a post-specific `cover.design` blueprint for image crop, contrast layers, headline placement, hook treatment, and footer; the validator requires that blueprint before a researched new cover can pass.

### Use An AI Scene Image As A Cover Background

```text
Generate a text-free rainy-day coffee-shop work scene, then use it as the background of an XHS cover for a freelance day-in-the-life post.
```

Scene images must contain **no embedded text or Chinese characters**, and the literal subject must be recognisable. The cover renderer is responsible for Chinese headline typography, preventing garbled text and inconsistent fonts.

For photo-led covers, export the post-specific image-generation request before producing the background:

```bash
python3 scripts/xhs-scene-prompt.py --input data/<date>-<keyword>/post-package.json --json
```

Use the returned prompt to create one new image, save it as `publish/background.png`, then pass it to `xhs-cover.py --background`. Never select a background from a fixed category template.

### Build A Carousel

```text
Turn “My first solo Japan trip: packing, transport, hotels, and traps to avoid” into a 6-slide XHS carousel.
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
| `scripts/xhs-cover-research.py` | Collect current high-engagement same-topic covers into a private reference sheet before each cover |
| `scripts/xhs-scene-prompt.py` | Turn each photo-led cover's unique visual direction into an image-generation prompt |
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
- Pillow, for assembling the private reference sheet; individual references still remain available if it is not installed
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
    ├── xhs-cover-research.py
    ├── xhs-scene-prompt.py
    ├── xhs-cover.py
    ├── xhs-carousel.py
    ├── xhs-style-check.py
    └── xhs-publish.py
```

## Notes

- XHS page structure and anti-bot measures can change. Re-run `xhs login` when research authentication expires.
- Publishing is an external action and requires explicit user approval of the final version.
- Never commit QR codes, cookies, creator-page login data, unapproved drafts, or test output.
- Never commit or upload third-party reference images inside `cover-research/`; they are private visual analysis only.

## License

[MIT](./LICENSE)
