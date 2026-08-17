# XHS Style QA

## Caption

- Can a reader understand the tension from the title and first three lines alone?
- Does it sound like a creator talking to a peer rather than a report introduction?
- Does every paragraph deepen the tension, give a useful action, or create a reason to keep reading?
- Is there a concrete action, comparison, or decision rule?
- Does the ending invite a specific response instead of ending in a slogan?
- Is the body exactly the approved final text? Do not publish a shortened preview.

## Cover

- Is the headline readable as a phone thumbnail?
- Is there one clear question, conflict, or outcome that earns a tap?
- Does the hook use a high-contrast block rather than blending into the page?
- Are there 2-3 headline lines, a small context badge, and enough breathing room?
- Does it look like an intentional XHS cover rather than a corporate slide or generic quote card?
- Does it promise the same topic the body answers?

## Final Version Lock

- Render the cover from the same `post-package.json` as the caption.
- After the user approves, run `xhs-style-check.py --write-lock` with that rendered cover.
- The lock hashes the exact title, full caption including tags, and cover file.
- `xhs-publish.py` verifies the lock before it opens the final publish action. Any text, tag, or cover change requires a new approval and new lock.
