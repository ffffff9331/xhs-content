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
    if not isinstance(cover, dict) or not str(cover.get("hook", "")).strip():
        errors.append("cover.hook is required")
    elif chinese_length(str(cover["hook"])) > 14:
        errors.append("cover.hook must be 14 characters or fewer")
    if not isinstance(cover, dict) or not str(cover.get("supporting", "")).strip():
        errors.append("cover.supporting is required")
    elif chinese_length(str(cover["supporting"])) > 20:
        errors.append("cover.supporting must be 20 characters or fewer")
    if not isinstance(cover, dict) or cover.get("style") != "xhs-bold":
        errors.append("cover.style must be xhs-bold; muted generic covers are not publishable")
    if not isinstance(cover, dict) or not str(cover.get("badge", "")).strip():
        errors.append("cover.badge is required for the XHS cover hierarchy")

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
