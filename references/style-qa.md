# XHS Style QA

## Caption

- Can a reader understand the tension from the title and first three lines alone?
- Does it sound like a creator talking to a peer rather than a report introduction?
- Does every paragraph deepen the tension, give a useful action, or create a reason to keep reading?
- Is there a concrete action, comparison, or decision rule?
- Does the ending invite a specific response instead of ending in a slogan?
- Is the body exactly the approved final text? Do not publish a shortened preview.

## Cover

- Before looking at the final cover, was a fresh same-topic XHS cover search completed for this exact post? The research may not be reused from a loosely related or old topic.
- Were 3–8 reference covers actually inspected at thumbnail scale, with the resulting patterns recorded in `cover.research`?
- Does the final cover borrow category-level conventions only, while changing the scene, copy, composition, and recognisable creator treatment? Reference images must never become final cover assets.
- Is the headline readable as a phone thumbnail?
- Is there one clear question, conflict, or outcome that earns a tap?
- Does the hook use a high-contrast block rather than blending into the page?
- Are there 2-3 headline lines, a small context badge, and enough breathing room?
- Does it look like an intentional XHS cover rather than a corporate slide or generic quote card?
- Does it promise the same topic the body answers?
- Can the reader identify the literal subject of the note before reading the words? A kitten post needs a kitten; a campus story needs a person/campus; a product review needs the actual product.
- Is the layout earned by the content? Use `photo-story` for a subject-led story, `photo-diary` for a lifestyle/personal memory, `product-focus` for a product/store/food/object/venue, `editorial` for a career/education/interview/point-of-view post, and `checklist` only when the note is genuinely a list, comparison, or process card.
- Does the background feel deliberately art-directed for this topic, rather than a generic illustration reused from another post?
- For every photo-led cover, does `cover.scene` name a fresh, text-free image prompt with topic-specific required elements and a negative prompt? Does the delivered background actually match it, rather than merely changing the caption on an older background?
- Does this topic have a deliberately different visual response from unrelated categories? The XHS feel should come from hierarchy and tension, not a fixed coral card pasted onto every industry.
- Can the final image be distinguished from an unrelated category even with the headline hidden? Verify that the per-post `cover.design` changes the image crop, text zones, contrast treatment, and emphasis instead of merely selecting another named template.

## Final Version Lock

- Render the cover from the same `post-package.json` as the caption.
- After the user approves, run `xhs-style-check.py --write-lock` with that rendered cover.
- The lock hashes the exact title, full caption including tags, and cover file.
- `xhs-publish.py` verifies the lock before it opens the final publish action. Any text, tag, or cover change requires a new approval and new lock.
