---
name: xhs-content
description: "Create and publish bold Xiaohongshu notes: research, captions, covers, carousels, and locked final versions."
---

# XHS Content Studio

Create a real publishable XHS note, not a generic article plus an unrelated poster. Use one `post-package.json` as the source of truth for the title, complete caption, hashtags, cover, carousel, and publication payload.

## Style Gate

Apply this gate to every generated caption and cover. Do not silently shorten user-approved copy.

- Write a **recognizable XHS caption**: emotionally direct title, hook in the first 1-3 lines, conversational Chinese, a usable point of view or action, short phone-readable paragraphs, and a specific invitation to comment.
- Render a **recognizable XHS cover**: a 3:4 vertical image with a scroll-stopping hierarchy at phone size. Use only the elements the category research earns: a raw food or lifestyle cover may need just 1–2 large lines over the scene, while a comparison may need a label and a high-contrast hook. Do not force every post into a badge + hook + footer stack.
- Make the cover **subject-led, not template-led**. Every new post needs `cover.visual`: a literal subject, mood, required on-image elements, text-safe area, and layout. A kitten post must visibly contain a kitten; a nursing post must show the relevant person or setting; a product post must show the product.
- Make the cover **category-informed, not taste-led**. Before every new cover, run `xhs-cover-research.py` with the exact topic and, when useful, one adjacent format query. Inspect the downloaded high-engagement cover sheet, record observed composition, typography, color, and subject-treatment patterns in `cover.research`, then turn them into a per-post `cover.design` blueprint. Research is incomplete when it is only metadata; it must alter the final cover structure.
- Match layout to the content: use `photo-story` for a subject-led scene, `photo-diary` for a lifestyle/personal memory, `product-focus` for a product, store, food, object, or venue, `editorial` for careers, education, interviews, or a strong point of view, and `checklist` only for a genuine checklist, comparison, or process card. Never reuse the generic checklist illustration for an unrelated narrative post.
- When the research indicates a scene-led cover, generate or obtain a text-free, rights-cleared scene image first, then add Chinese typography with `xhs-cover.py --background`. When the research indicates a text-led opinion cover, `cover.design` may deliberately render without a background image. Do not force either treatment onto the other.
- Choose a researched category-specific contrast pair in `cover.palette`, with only one secondary accent. The XHS constant is confident hierarchy, not one fixed coral palette. Avoid gradients, tiny text, bland one-color covers, and dense decoration.
- Keep cover and caption aligned, but make the cover sell the question while the caption answers it.
- Treat a user-approved caption as immutable. A short variant is allowed only after the user explicitly requests one and it is packaged separately with `mode: "short"`.
- Set `cover.style` to `xhs-bold`. The validator and renderer reject a generic or muted cover package.
- Run `python3 scripts/xhs-style-check.py --input <post-package.json> --strict --require-visual --require-cover-research` before delivery. Read [references/style-qa.md](references/style-qa.md) for editorial decisions.

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
3. Before making the cover, collect and inspect current same-category XHS covers. The reference files are private visual research only and must never be used as the finished cover image:

```bash
python3 scripts/xhs-cover-research.py \
  --keyword "<exact topic>" \
  --keyword "<topic + format/intent>" \
  --out-dir "data/<date>-<keyword>/cover-research"
```

4. Add a subject-led `cover.visual` brief, `cover.research`, and a `cover.design` blueprint to the package. `cover.research` identifies 3–8 inspected note IDs, documents observed patterns, and states the original differentiation direction. `cover.design` is the post-specific image placement, text zones, panels, and emphasis treatment; do not select a fixed named template as the creative decision.
5. Run the style check with `--require-visual --require-cover-research`.
6. Turn the post-specific scene brief into an image-generation prompt, then use the available image-generation tool to create a **new text-free 3:4 scene image**. Do not reuse a scene from a different note:

```bash
python3 scripts/xhs-scene-prompt.py --input "<post-package.json>" --json
```

7. Render the cover:

```bash
python3 scripts/xhs-cover.py \
  --input "<post-package.json>" \
  --background "<text-free-subject-scene>" \
  --out-dir "<output-dir>"
```

7. Present the exact title, full caption, tags, and `cover.png` together. Never present a shortened preview as final content.

### Cover Reference Research And Scene Images

Every cover starts with same-category reference research, whether it uses a photographic scene, generated image, or checklist layout. Use an available image-generation tool or image skill first for the **new**, text-free final scene.

- Search the exact subject first, then add one format-specific query when it changes the visual language, for example `幼猫到家` + `接猫清单`, or `在职考研` + `考研作息`.
- Inspect `cover-reference-wall.html` at phone-thumbnail scale, or `cover-reference-sheet.jpg` when present. Extract visual rules, not assets: focal-subject placement, degree of cropping, headline density, color temperature, badge treatment, and whether the top notes are photo-first or information-first.
- Never publish reference files, use their images as final backgrounds, imitate a recognisable creator layout, or reuse their exact headline wording. The final cover should keep the category's readable conventions while changing scene, text, and composition.
- Record what was inspected and the original art direction in `cover.research`. Do not invent a research record if collection failed; ask the user to restore login or explicitly approve a no-research draft.

- Generate a clean image with no embedded text or Chinese characters. The literal subject from `cover.visual.required_elements` must be visible at phone size.
- For every photo-led cover, put the new image request in `cover.scene`. It must name the literal scene, camera treatment, location, action, light, calm text-safe area, and a topic-specific negative prompt. Run `xhs-scene-prompt.py` to produce the exact image-generation payload, generate a new bitmap, and save it alongside this post. The image is not optional just because `cover.design` is custom.
- Choose `photo-story` when the subject is the story, `photo-diary` for a softer lifestyle/personal post, `product-focus` when the object/venue is the promise, and `editorial` when a person, profession, or opinion needs authority. Use `checklist` only for a real checklist. Do not default to the same visual treatment across unrelated topics.
- Use the deterministic cover renderer for Chinese typography and hierarchy. Keep a text-safe area in the generated image:

```bash
python3 scripts/xhs-cover.py \
  --input "<post-package.json>" \
  --background "<text-free-scene-image>" \
  --out-dir "<output-dir>"
```
- Default to one cover. Create a carousel only when requested or when multiple slides materially improve the explanation.
- If no image-generation tool is available, use a rights-cleared, subject-relevant scene image when possible. If that is not available, use a content-specific illustration only for the requested subject; do not silently substitute the generic checklist cover for a story-led note.

### Carousel

Use when the user asks for multiple pages or a step-by-step visual explanation.

1. Read [references/carousel.md](references/carousel.md).
2. Make a 2-10 page carousel plan; the first slide must pass the Style Gate.
3. Run `python3 scripts/xhs-carousel.py --input "<carousel.json>" --out-dir "<output-dir>"`.

### Publish The Final Approved Image Note

Only publish after the user explicitly approves the exact title, complete caption, hashtags, cover, visibility, and timing.

**Automatic publishing has account-risk and account-penalty risk and is not the recommended workflow.** Prefer that the user uploads the locked title, full caption, hashtags, and cover manually in the creator page. Never use automatic publishing for unattended, scheduled, bulk, multi-account, or interaction automation.

If the user explicitly still requests automatic publishing, show this warning before running the publisher and obtain a separate, unambiguous acknowledgement of that risk. Normal approval of the post content is not enough.

1. Render the approved cover from the package.
2. Lock the approved version. This creates hashes for the title, **complete caption including tags**, and cover image:

```bash
python3 scripts/xhs-style-check.py \
  --input "<post-package.json>" \
  --cover "<output-dir>/cover.png" \
  --strict --require-visual --require-cover-research --write-lock
```

3. Publish only the locked version:

```bash
python3 scripts/xhs-publish.py \
  --input "<post-package.json>" \
  --cover "<output-dir>/cover.png" \
  --publish --acknowledge-automation-risk
```

The publisher repeats the risk warning and refuses to run without `--acknowledge-automation-risk`. It targets the current creator page’s `上传图文` tab and `xhs-publish-btn[is-publish="true"]` control, not the old plain-text button selector. It refuses publication if the version lock is missing or does not match. It keeps public/immediate defaults unless the user explicitly requests a different visibility or schedule. Treat publication as successful only on `published=true` or another explicit success state. Stop for CAPTCHA, login, policy declarations, or unexpected dialogs and ask the user to take over.

## Output Layout

```text
data/<date>-<keyword>/
  sources.jsonl
  report.md
  drafts.md
  cover-research/
    cover-references.json
    cover-reference-wall.html
    cover-reference-sheet.jpg
    reference-covers/
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
- `scripts/xhs-cover-research.py`: current high-engagement same-category cover reference collection.
- `scripts/xhs-cover.py`: one bold, text-safe XHS cover.
- `scripts/xhs-carousel.py`: multi-page carousel renderer.
- `scripts/xhs-style-check.py`: style and final-version validation.
- `scripts/xhs-publish.py`: locked-package image-note publisher.
