#!/usr/bin/env python3
"""Validate the editorial and cover contract of an XHS post package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


REPORT_WORDS = ("首先", "其次", "最后", "综上所述", "总结一下", "赋能", "驱动", "赛道", "底层逻辑", "抓手")
HOOK_MARKERS = ("？", "?", "别", "先", "救命", "劝退", "还能", "到底", "为什么", "怎么")


def chinese_length(value: str) -> int:
    return len(re.sub(r"\s", "", value))


def full_caption(package: dict) -> str:
    body = str(package["body"]).strip()
    tags = package.get("hashtags", [])
    return body + ("\n\n" + " ".join(f"#{tag}" for tag in tags) if tags else "")


def digest(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Check XHS post-package.json before delivery or publication.")
    parser.add_argument("--input", required=True, help="Path to post-package.json")
    parser.add_argument("--strict", action="store_true", help="Treat editorial warnings as errors")
    parser.add_argument(
        "--require-visual",
        action="store_true",
        help="Require a content-aware cover.visual brief for newly created covers",
    )
    parser.add_argument(
        "--require-cover-research",
        action="store_true",
        help="Require current same-topic XHS cover research before creating a new cover",
    )
    parser.add_argument("--cover", help="Rendered cover file used for final-lock verification")
    parser.add_argument("--write-lock", action="store_true", help="Write an approved final-version lock")
    parser.add_argument("--verify-lock", action="store_true", help="Require the existing final-version lock to match")
    args = parser.parse_args()

    package = json.loads(Path(args.input).read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []
    title = str(package.get("title", "")).strip()
    body = str(package.get("body", "")).strip()
    tags = package.get("hashtags", [])
    cover = package.get("cover", {})
    design = cover.get("design") if isinstance(cover, dict) else None
    mode = package.get("mode", "standard")

    if not title:
        errors.append("title is required")
    elif chinese_length(title) > 20:
        errors.append("title exceeds 20 characters")
    elif not any(marker in title for marker in ("？", "?", "！", "!", "🆘", "救命", "别", "到底")):
        warnings.append("title may lack a recognizable XHS tension or hook")

    if not body:
        errors.append("body is required")
    else:
        first_line = next((line.strip() for line in body.splitlines() if line.strip()), "")
        if chinese_length(first_line) > 48:
            warnings.append("opening line is too long for a phone-first hook")
        if not any(marker in first_line for marker in HOOK_MARKERS):
            warnings.append("opening line may not establish a clear XHS hook")
        expected_min, expected_max = (50, 300) if mode == "short" else (180, 800)
        length = chinese_length(body)
        if not expected_min <= length <= expected_max:
            warnings.append(f"body length {length} is outside the suggested {mode} range {expected_min}-{expected_max}")
        for word in REPORT_WORDS:
            if word in body:
                warnings.append(f"body contains report-like wording: {word}")
        closing = "".join(line.strip() for line in body.splitlines()[-3:])
        if not any(marker in closing for marker in ("？", "?", "评论", "说说", "你是", "报个到")):
            warnings.append("ending may lack a specific XHS-style interaction prompt")

    if not isinstance(tags, list) or not 3 <= len(tags) <= 8:
        errors.append("hashtags must contain 3 to 8 plain tag names")
    elif any(not isinstance(tag, str) or not tag.strip() or tag.startswith("#") for tag in tags):
        errors.append("hashtags must be non-empty plain names without #")

    headline = cover.get("headline", []) if isinstance(cover, dict) else []
    if not isinstance(headline, list) or not 2 <= len(headline) <= 3:
        errors.append("cover.headline must contain 2 or 3 lines")
    elif any(chinese_length(str(line)) > 13 for line in headline):
        errors.append("each cover headline line must be 13 characters or fewer")
    def hides(element: str) -> bool:
        section = design.get(element) if isinstance(design, dict) else None
        return isinstance(section, dict) and section.get("visible") is False

    if not hides("hook") and (not isinstance(cover, dict) or not str(cover.get("hook", "")).strip()):
        errors.append("cover.hook is required")
    elif not hides("hook") and chinese_length(str(cover["hook"])) > 14:
        errors.append("cover.hook must be 14 characters or fewer")
    if not hides("supporting") and (not isinstance(cover, dict) or not str(cover.get("supporting", "")).strip()):
        errors.append("cover.supporting is required")
    elif not hides("supporting") and chinese_length(str(cover["supporting"])) > 20:
        errors.append("cover.supporting must be 20 characters or fewer")
    if not isinstance(cover, dict) or cover.get("style") != "xhs-bold":
        errors.append("cover.style must be xhs-bold; muted generic covers are not publishable")
    if not hides("badge") and (not isinstance(cover, dict) or not str(cover.get("badge", "")).strip()):
        errors.append("cover.badge is required for the XHS cover hierarchy")

    palette = cover.get("palette") if isinstance(cover, dict) else None
    if palette is not None:
        if not isinstance(palette, dict):
            errors.append("cover.palette must be an object of researched category colors")
        else:
            for key in ("ink", "muted", "accent", "soft", "softest", "warm"):
                value = palette.get(key)
                if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
                    errors.append(f"cover.palette.{key} must be a six-digit hex color")

    visual = cover.get("visual") if isinstance(cover, dict) else None
    if args.require_visual and not isinstance(visual, dict):
        errors.append("cover.visual is required for new subject-led covers")
    if isinstance(visual, dict):
        layout = visual.get("layout", "auto")
        if layout not in {"auto", "photo-story", "photo-diary", "product-focus", "editorial", "checklist"}:
            errors.append(
                "cover.visual.layout must be auto, photo-story, photo-diary, product-focus, editorial, or checklist"
            )
        if not str(visual.get("subject", "")).strip():
            errors.append("cover.visual.subject must name the actual subject shown on the cover")
        elements = visual.get("required_elements", [])
        if not isinstance(elements, list) or not elements or any(not str(item).strip() for item in elements):
            errors.append("cover.visual.required_elements must list the subject details the image must show")
        if layout in {"photo-story", "photo-diary", "product-focus", "editorial"} and not str(visual.get("text_safe_area", "")).strip():
            errors.append("photo-led covers must declare cover.visual.text_safe_area")
        composition = visual.get("composition")
        if composition is not None and composition not in {"full-bleed", "split-panel", "framed-photo", "lower-panel", "checklist-grid"}:
            errors.append("cover.visual.composition must be full-bleed, split-panel, framed-photo, lower-panel, or checklist-grid")
        treatment = visual.get("headline_treatment")
        if treatment is not None and treatment not in {"solid", "outline", "label"}:
            errors.append("cover.visual.headline_treatment must be solid, outline, or label")

    scene = cover.get("scene") if isinstance(cover, dict) else None
    photo_layouts = {"photo-story", "photo-diary", "product-focus", "editorial"}
    visual_layout = visual.get("layout") if isinstance(visual, dict) else None
    design_image = design.get("image", {}) if isinstance(design, dict) and isinstance(design.get("image"), dict) else {}
    uses_subject_scene = design_image.get("visible", True) is not False
    if args.require_visual and visual_layout in photo_layouts and uses_subject_scene:
        if not isinstance(scene, dict):
            errors.append("cover.scene is required for photo-led covers; it must specify the unique image-generation brief")
        else:
            if not str(scene.get("prompt", "")).strip():
                errors.append("cover.scene.prompt must describe this post's literal, text-free scene")
            if not str(scene.get("negative_prompt", "")).strip():
                errors.append("cover.scene.negative_prompt must rule out embedded text, logos, and unrelated subjects")
            if scene.get("aspect_ratio") != "3:4":
                errors.append("cover.scene.aspect_ratio must be 3:4")
            if not str(scene.get("subject_visibility", "")).strip():
                errors.append("cover.scene.subject_visibility must explain how the literal subject stays visible at thumbnail size")

    research = cover.get("research") if isinstance(cover, dict) else None
    if args.require_cover_research and not isinstance(research, dict):
        errors.append("cover.research is required; inspect current same-topic XHS cover references first")
    if args.require_cover_research and palette is None:
        errors.append("cover.palette is required; choose a category-specific palette from cover research")
    if args.require_cover_research and not isinstance(design, dict):
        errors.append("cover.design is required; render a per-post visual blueprint instead of selecting a fixed layout")
    if isinstance(design, dict):
        if design.get("mode") != "custom":
            errors.append("cover.design.mode must be custom")
        image = design.get("image")
        if not isinstance(image, dict):
            errors.append("cover.design.image must place the subject image for this post")
        headline_design = design.get("headline")
        if not isinstance(headline_design, dict):
            errors.append("cover.design.headline must define this post's title placement")
        badge_design = design.get("badge")
        if not isinstance(badge_design, dict):
            errors.append("cover.design.badge must define this post's context label placement")
    if isinstance(research, dict):
        if not str(research.get("query", "")).strip():
            errors.append("cover.research.query must identify the same-topic XHS search")
        note_ids = research.get("inspected_note_ids", [])
        if not isinstance(note_ids, list) or not 3 <= len(note_ids) <= 8 or any(not str(item).strip() for item in note_ids):
            errors.append("cover.research.inspected_note_ids must contain 3 to 8 inspected reference notes")
        patterns = research.get("patterns", {})
        if not isinstance(patterns, dict):
            errors.append("cover.research.patterns must record observed cover patterns")
        else:
            for key in ("composition", "typography", "color", "subject_treatment"):
                values = patterns.get(key, [])
                if not isinstance(values, list) or not values or any(not str(item).strip() for item in values):
                    errors.append(f"cover.research.patterns.{key} must record at least one observed pattern")
        if not str(research.get("differentiation", "")).strip():
            errors.append("cover.research.differentiation must explain how this cover stays original")

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    if errors or (args.strict and warnings):
        sys.exit(1)

    if args.write_lock or args.verify_lock:
        if not args.cover:
            raise SystemExit("--cover is required when writing or verifying a final-version lock")
        cover_path = Path(args.cover)
        if not cover_path.is_file():
            raise SystemExit(f"Cover does not exist: {cover_path}")
        lock = {
            "title_sha256": digest(title),
            "caption_sha256": digest(full_caption(package)),
            "cover_sha256": digest(cover_path.read_bytes()),
        }
        if args.write_lock:
            package["approval_lock"] = lock
            Path(args.input).write_text(
                json.dumps(package, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print("LOCKED: title, complete caption, tags, and cover are bound for publication")
        if args.verify_lock:
            if package.get("approval_lock") != lock:
                raise SystemExit("Final-version lock does not match the current title, full caption, tags, or cover")
            print("LOCK VERIFIED: publishing payload exactly matches the approved version")
    print("PASS: post package satisfies the XHS content and cover contract")


if __name__ == "__main__":
    main()
