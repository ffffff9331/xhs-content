#!/usr/bin/env python3
"""Turn a cover's subject-led scene brief into an ImageGen-ready prompt.

This script deliberately produces a new prompt from the post package rather
than selecting a category template. The caller still uses its available image
generation tool to create the bitmap, then hands the resulting text-free image
to xhs-cover.py for Chinese typography.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PHOTO_LAYOUTS = {"photo-story", "photo-diary", "product-focus", "editorial"}


def required(value: object, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise SystemExit(f"Missing {label}")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Print an ImageGen-ready, per-post XHS scene prompt.")
    parser.add_argument("--input", required=True, help="Path to post-package.json")
    parser.add_argument("--json", action="store_true", help="Emit a JSON prompt payload instead of plain text")
    args = parser.parse_args()

    package = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cover = package.get("cover", {})
    visual = cover.get("visual", {}) if isinstance(cover.get("visual"), dict) else {}
    layout = visual.get("layout")
    if layout not in PHOTO_LAYOUTS:
        raise SystemExit("A scene prompt is only required for photo-led cover layouts")
    scene = cover.get("scene", {}) if isinstance(cover.get("scene"), dict) else {}
    prompt = required(scene.get("prompt"), "cover.scene.prompt")
    negative = required(scene.get("negative_prompt"), "cover.scene.negative_prompt")
    ratio = required(scene.get("aspect_ratio"), "cover.scene.aspect_ratio")
    if ratio != "3:4":
        raise SystemExit("cover.scene.aspect_ratio must be 3:4")
    visibility = required(scene.get("subject_visibility"), "cover.scene.subject_visibility")
    elements = visual.get("required_elements", [])
    if not isinstance(elements, list) or not elements:
        raise SystemExit("cover.visual.required_elements is required")

    full_prompt = (
        f"Create one original vertical {ratio} image for a Xiaohongshu cover. "
        f"Literal subject and required visible details: {', '.join(str(item).strip() for item in elements)}. "
        f"Art direction: {prompt} "
        f"Thumbnail-readability requirement: {visibility} "
        f"Leave the {required(visual.get('text_safe_area'), 'cover.visual.text_safe_area')} area visually calm for later Chinese typography. "
        "Use real, specific material detail and a coherent single scene. The image must contain no embedded words."
    )
    payload = {
        "aspect_ratio": ratio,
        "prompt": full_prompt,
        "negative_prompt": negative,
        "render_note": "Generate only the text-free bitmap. Render Chinese headline, badge, and hook afterward with xhs-cover.py.",
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(full_prompt)
        print(f"\nNegative prompt: {negative}")
        print("\nOutput: one text-free 3:4 bitmap; do not add title text, watermarks, or logos.")


if __name__ == "__main__":
    main()
