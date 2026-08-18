#!/usr/bin/env python3
"""Collect high-engagement XHS cover references for one cover-creation task.

References are for visual analysis only. They must not be republished, copied,
or used as the final cover background.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


def log(message: str) -> None:
    print(f"[xhs-cover-research] {message}", file=sys.stderr, flush=True)


def parse_count(value: object) -> int:
    text = str(value or "0").replace(",", "").strip().lower()
    try:
        if "万" in text or text.endswith("w"):
            return round(float(text.replace("万", "").replace("w", "")) * 10000)
        if text.endswith("k"):
            return round(float(text[:-1]) * 1000)
        return int(text)
    except ValueError:
        return 0


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-")
    return cleaned[:36] or "cover"


def run_xhs(args: list[str], timeout: int = 90) -> str:
    try:
        result = subprocess.run(["xhs", *args], capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as error:
        raise SystemExit("xhs-cli is required. Install it, then run xhs login.") from error
    except subprocess.TimeoutExpired as error:
        raise SystemExit(f"xhs-cli timed out while running: {' '.join(args)}") from error
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "unknown xhs-cli error").strip()
        raise SystemExit(message[:500])
    return result.stdout


def cover_url(note_card: dict) -> str:
    cover = note_card.get("cover", {})
    if isinstance(cover, dict) and cover.get("urlDefault"):
        return str(cover["urlDefault"])
    images = note_card.get("imageList", [])
    if images and isinstance(images[0], dict):
        infos = images[0].get("infoList", [])
        if infos and isinstance(infos[0], dict):
            return str(infos[0].get("url", ""))
    return ""


def collect(keyword: str, limit: int) -> list[dict]:
    raw = run_xhs(["search", keyword, "--json"])
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SystemExit("xhs-cli returned invalid search JSON") from error

    notes: list[dict] = []
    for entry in entries[:limit]:
        card = entry.get("noteCard", {})
        interact = card.get("interactInfo", {})
        user = card.get("user", {})
        note_id = str(entry.get("id", ""))
        likes = parse_count(interact.get("likedCount"))
        favorites = parse_count(interact.get("collectedCount"))
        comments = parse_count(interact.get("commentCount"))
        shares = parse_count(interact.get("sharedCount"))
        image = cover_url(card)
        if not note_id or not image:
            continue
        notes.append(
            {
                "note_id": note_id,
                "title": str(card.get("displayTitle", "")).strip(),
                "author": str(user.get("nickname") or user.get("nickName") or "").strip(),
                "cover_url": image,
                "likes": likes,
                "favorites": favorites,
                "comments": comments,
                "shares": shares,
                "engagement_score": likes + favorites * 2 + comments * 8 + shares * 3,
                "source_query": keyword,
                "note_type": str(card.get("type", entry.get("type", ""))),
                "url": f"https://www.xiaohongshu.com/explore/{note_id}",
            }
        )
    return notes


def download_cover(url: str, destination: Path) -> str:
    secure_url = url.replace("http://", "https://", 1)
    request = Request(secure_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(request, timeout=30) as response:
            destination.write_bytes(response.read())
        return ""
    except (URLError, OSError) as error:
        return str(error)


def make_contact_sheet(items: list[dict], directory: Path) -> str:
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        return "Pillow is unavailable; inspect the individual files in reference-covers/."

    columns, thumb_width, thumb_height, label_height, gap = 3, 244, 326, 48, 24
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * thumb_width + (columns + 1) * gap, rows * (thumb_height + label_height) + (rows + 1) * gap), "#FFF8F3")
    draw = ImageDraw.Draw(canvas)
    for position, item in enumerate(items):
        image_path = directory / item["reference_file"]
        if not image_path.is_file():
            continue
        try:
            with Image.open(image_path) as source:
                picture = ImageOps.fit(source.convert("RGB"), (thumb_width, thumb_height), method=Image.Resampling.LANCZOS)
        except (OSError, ValueError):
            continue
        column, row = position % columns, position // columns
        x = gap + column * (thumb_width + gap)
        y = gap + row * (thumb_height + label_height + gap)
        canvas.paste(picture, (x, y))
        draw.rectangle((x, y + thumb_height, x + thumb_width, y + thumb_height + label_height), fill="#123C3E")
        draw.text((x + 10, y + thumb_height + 15), f"#{position + 1}  {item['likes']:,} likes", fill="#FFFFFF")
    canvas.save(directory.parent / "cover-reference-sheet.jpg", quality=92)
    return ""


def write_reference_wall(items: list[dict], output: Path) -> None:
    cards: list[str] = []
    for index, item in enumerate(items, start=1):
        title = html.escape(item["title"] or "无标题封面")
        query = html.escape(item["source_query"])
        filename = html.escape(f"reference-covers/{item['reference_file']}")
        cards.append(
            f'''<article class="card">
  <img src="{filename}" alt="Reference cover {index}: {title}">
  <div class="meta"><strong>#{index}</strong><span>{item['likes']:,} likes</span></div>
  <p>{title}</p><small>{query}</small>
</article>'''
        )
    page = f'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>封面赛道参考</title>
<style>
body{{margin:0;background:#fff8f3;color:#143c3e;font:15px/1.45 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}
main{{max-width:1200px;margin:auto;padding:28px}}h1{{margin:0 0 8px}}.notice{{color:#6a7778;margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:18px}}.card{{margin:0;background:#fff;border:1px solid #f0e3dc;overflow:hidden}}
img{{display:block;width:100%;aspect-ratio:3/4;object-fit:cover;background:#f3eee9}}.meta{{display:flex;justify-content:space-between;padding:10px 12px 0;color:#ef5b4d}}p{{margin:8px 12px 4px;font-weight:700}}small{{display:block;margin:0 12px 14px;color:#6a7778}}
</style><main><h1>封面赛道参考</h1><p class="notice">仅供本次视觉分析。不得复用、抄袭、发布或作为最终封面底图。</p><section class="grid">{''.join(cards)}</section></main></html>'''
    (output / "cover-reference-wall.html").write_text(page, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect current XHS cover references before creating a cover.")
    parser.add_argument("--keyword", action="append", required=True, help="One topic or adjacent-format search term. Repeatable.")
    parser.add_argument("--out-dir", required=True, help="Directory for private reference artifacts.")
    parser.add_argument("--limit", type=int, default=30, help="Search results inspected per query.")
    parser.add_argument("--top", type=int, default=8, help="High-engagement covers to download for visual inspection.")
    args = parser.parse_args()

    run_xhs(["status"], timeout=15)
    output = Path(args.out_dir)
    images = output / "reference-covers"
    images.mkdir(parents=True, exist_ok=True)
    all_notes: dict[str, dict] = {}
    for keyword in args.keyword:
        log(f"searching: {keyword}")
        for item in collect(keyword.strip(), args.limit):
            existing = all_notes.get(item["note_id"])
            if existing is None or item["engagement_score"] > existing["engagement_score"]:
                all_notes[item["note_id"]] = item

    ranked = sorted(all_notes.values(), key=lambda item: item["engagement_score"], reverse=True)[: args.top]
    if not ranked:
        raise SystemExit("No XHS cover references were found. Confirm the query and xhs login, then try again.")
    for index, item in enumerate(ranked, start=1):
        filename = f"{index:02d}-{safe_name(item['note_id'])}.webp"
        item["reference_file"] = filename
        item["download_error"] = download_cover(item["cover_url"], images / filename)
        if item["download_error"]:
            log(f"could not download reference #{index}: {item['download_error']}")

    payload = {
        "purpose": "Private visual research only. Do not publish, reproduce, or use these reference images as the final cover.",
        "queries": args.keyword,
        "selection": "Ranked by likes, favorites, comments, and shares from current XHS search results.",
        "references": ranked,
    }
    (output / "cover-references.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# 封面赛道参考",
        "",
        "> 仅供本次视觉分析。不得复用、抄袭、发布或作为最终封面底图。",
        "",
        f"检索词：{' / '.join(args.keyword)}",
        "",
        "先查看 `cover-reference-sheet.jpg` 和 `reference-covers/`，再在 post-package.json 记录拆解后的视觉规律与差异化方向。",
        "",
        "| 排名 | 标题 | 互动分 | 检索词 |",
        "| --- | --- | ---: | --- |",
    ]
    for index, item in enumerate(ranked, start=1):
        title = item["title"].replace("|", " ") or "（无标题封面）"
        lines.append(f"| {index} | {title} | {item['engagement_score']:,} | {item['source_query']} |")
    (output / "cover-research.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_reference_wall(ranked, output)
    sheet_error = make_contact_sheet(ranked, images)
    if sheet_error:
        log(sheet_error)
    print(f"Collected {len(ranked)} private cover references in {output}")


if __name__ == "__main__":
    main()
