---
name: xhs-content
description: "Create and publish bold Xiaohongshu notes: research, captions, covers, carousels, and locked final versions."
---

# XHS Content Studio

Create a real publishable XHS note, not a generic article plus an unrelated poster. Use one `post-package.json` as the source of truth for the title, complete caption, hashtags, cover, carousel, and publication payload.

## Style Gate

Apply this gate to every generated caption and cover. Do not silently shorten user-approved copy.

- Write a **recognizable XHS caption**: emotionally direct title, hook in the first 1-3 lines, conversational Chinese, a usable point of view or action, short phone-readable paragraphs, and a specific invitation to comment.
- Render a **recognizable XHS cover**: a 3:4 vertical cover with 2-3 large headline lines, one high-contrast hook, a small context badge, and strong hierarchy. Make it scroll-stopping at phone size, not a muted PPT slide or caption screenshot.
- Use a confident contrast pair such as coral + ink + warm white, with only one secondary accent. Avoid gradients, tiny text, bland one-color covers, and dense decoration.
- Keep cover and caption aligned, but make the cover sell the question while the caption answers it.
- Treat a user-approved caption as immutable. A short variant is allowed only after the user explicitly requests one and it is packaged separately with `mode: "short"`.
- Set `cover.style` to `xhs-bold`. The validator and renderer reject a generic or muted cover package.
- Run `python3 scripts/xhs-style-check.py --input <post-package.json> --strict` before delivery. Read [references/style-qa.md](references/style-qa.md) for editorial decisions.

## Workflows

### Research And Topic Planning

Use when the user asks what is trending, wants inspiration, or needs a data-informed topic.

1. Run `python3 scripts/xhs-search.py --keyword "<keyword>" --limit 30`.
2. Save returned notes as `data/<date>-<keyword>/sources.jsonl`.
3. Write `report.md` with topic heat, recurring hooks, comment questions, top-note summaries, differentiated angles, and a source table.
4. Ground claims in the report. Require official verification for school admissions, fees, policy, medical, salary, and employment claims.

### Caption + One Cover (Default)

Use for ordinary requests such as “做一篇小红书笔记” or “给我文案和封面”. Unless the user explicitly requests text only, create a complete caption and exactly one cover.

1. Read [references/prompt.md](references/prompt.md).
2. Create `post-package.json` using [references/post-package.md](references/post-package.md).
3. Run the style check.
4. Render the cover:

```bash
python3 scripts/xhs-cover.py --input "<post-package.json>" --out-dir "<output-dir>"
```

5. Present the exact title, full caption, tags, and `cover.png` together. Never present a shortened preview as final content.

### Optional Scene Image / Supporting Images

Use when the user asks for a person, campus, hospital, product, lifestyle scene, or another photographic image. Use an available image-generation tool or image skill first.

- Generate a clean image with no embedded text or Chinese characters.
- Use the deterministic cover renderer for Chinese typography and hierarchy. Keep a text-safe area in the generated image:

```bash
python3 scripts/xhs-cover.py \
  --input "<post-package.json>" \
  --background "<text-free-scene-image>" \
  --out-dir "<output-dir>"
```
- Default to one cover. Create a carousel only when requested or when multiple slides materially improve the explanation.
- If no image-generation tool is available, fall back to the deterministic `xhs-cover.py` illustration instead of fabricating an external-image capability.

### Carousel

Use when the user asks for multiple pages or a step-by-step visual explanation.

1. Read [references/carousel.md](references/carousel.md).
2. Make a 2-10 page carousel plan; the first slide must pass the Style Gate.
3. Run `python3 scripts/xhs-carousel.py --input "<carousel.json>" --out-dir "<output-dir>"`.

### Publish The Final Approved Image Note

Only publish after the user explicitly approves the exact title, complete caption, hashtags, cover, visibility, and timing.

1. Render the approved cover from the package.
2. Lock the approved version. This creates hashes for the title, **complete caption including tags**, and cover image:

```bash
python3 scripts/xhs-style-check.py \
  --input "<post-package.json>" \
  --cover "<output-dir>/cover.png" \
  --strict --write-lock
```

3. Publish only the locked version:

```bash
python3 scripts/xhs-publish.py \
  --input "<post-package.json>" \
  --cover "<output-dir>/cover.png" \
  --publish
```

The publisher targets the current creator page’s `上传图文` tab and `xhs-publish-btn[is-publish="true"]` control, not the old plain-text button selector. It refuses publication if the version lock is missing or does not match. It keeps public/immediate defaults unless the user explicitly requests a different visibility or schedule. Treat publication as successful only on `published=true` or another explicit success state. Stop for CAPTCHA, login, policy declarations, or unexpected dialogs and ask the user to take over.

## Output Layout

```text
data/<date>-<keyword>/
  sources.jsonl
  report.md
  drafts.md
  post-package.json
  publish/
    cover.svg
    cover.png
    carousel/
```

Text-only is the sole exception to the cover requirement. Apply the caption rules and state explicitly that no image was requested.

## Resources

- [references/prompt.md](references/prompt.md): XHS voice and structure.
- [references/post-package.md](references/post-package.md): post package schema.
- [references/style-qa.md](references/style-qa.md): editorial and cover QA.
- [references/carousel.md](references/carousel.md): carousel planning rules.
- `scripts/xhs-search.py`: XHS topic collection.
- `scripts/xhs-cover.py`: one bold, text-safe XHS cover.
- `scripts/xhs-carousel.py`: multi-page carousel renderer.
- `scripts/xhs-style-check.py`: style and final-version validation.
- `scripts/xhs-publish.py`: locked-package image-note publisher.
