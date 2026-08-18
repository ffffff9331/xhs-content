#!/usr/bin/env python3
"""XHS (小红书) search via xhs-cli.

Uses xhs-cli (https://github.com/jackwener/xhs-cli) for data collection.
xhs-cli uses camoufox (anti-fingerprint Firefox) + window.__INITIAL_STATE__
extraction — no DOM scraping needed.

Prerequisites:
    pipx install xhs-cli   # or: uv tool install xhs-cli
    xhs login               # QR code / cookie / auto-extract from Chrome

Usage:
    python3 xhs-search.py --keyword "AI agents" --limit 30
    python3 xhs-search.py --keyword "Claude" --limit 20

Output: JSON array to stdout (stderr for logs)
"""

import argparse
import json
import subprocess
import sys


def log(msg):
    """Log to stderr (stdout is reserved for JSON output)."""
    print(f"[xhs-search] {msg}", file=sys.stderr, flush=True)


def run_xhs(args, timeout=120):
    """Run an xhs-cli command. Returns parsed JSON or None."""
    cmd = ["xhs"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            log(f"xhs-cli error ({args[0]}): {stderr[:300]}")
            return None
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        log(f"xhs-cli timed out ({args[0]}, {timeout}s)")
        return None
    except FileNotFoundError:
        log("xhs-cli not found — install with: pipx install xhs-cli")
        sys.exit(1)


def check_login():
    """Check if xhs-cli is logged in."""
    result = run_xhs(["status"], timeout=10)
    return result is not None


def parse_count(s):
    """Parse count string like '1.2万', '3k', '593' to int."""
    if not s:
        return 0
    s = str(s).replace(",", "").strip()
    if "万" in s or "w" in s:
        return round(float(s.replace("万", "").replace("w", "")) * 10000)
    if "k" in s or "K" in s:
        return round(float(s.replace("k", "").replace("K", "")) * 1000)
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0


def search_xhs(keyword, limit=30):
    """Search XHS for posts matching keyword, fetch detail for top posts."""

    # Step 1: Check login
    if not check_login():
        log("Not logged in. Run: xhs login")
        return []

    # Step 2: Search
    log(f"Searching XHS for: {keyword}")
    raw = run_xhs(["search", keyword, "--json"], timeout=120)
    if not raw:
        log("No search results")
        return []

    try:
        search_results = json.loads(raw)
    except json.JSONDecodeError:
        log(f"Failed to parse search JSON: {raw[:200]}")
        return []

    log(f"Search returned {len(search_results)} results")

    # Step 3: Extract basic info from search results, sort by likes
    cards = []
    for item in search_results:
        note_card = item.get("noteCard", {})
        interact = note_card.get("interactInfo", {})
        user = note_card.get("user", {})
        corner = note_card.get("cornerTagInfo", [])

        note_id = item.get("id", "")
        cover = note_card.get("cover", {})
        image_list = note_card.get("imageList", [])
        cover_url = cover.get("urlDefault", "") if isinstance(cover, dict) else ""
        if not cover_url and image_list and isinstance(image_list[0], dict):
            info_list = image_list[0].get("infoList", [])
            if info_list and isinstance(info_list[0], dict):
                cover_url = info_list[0].get("url", "")
        published = ""
        for tag in corner:
            if tag.get("type") == "publish_time":
                published = tag.get("text", "")

        cards.append({
            "note_id": note_id,
            "title": note_card.get("displayTitle", ""),
            "author": user.get("nickname", ""),
            "likes": parse_count(interact.get("likedCount", "0")),
            "favorites": parse_count(interact.get("collectedCount", "0")),
            "comments": parse_count(interact.get("commentCount", "0")),
            "shares": parse_count(interact.get("sharedCount", "0")),
            "published": published,
            "url": f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else "",
            "cover_url": cover_url,
            "cover_width": cover.get("width", 0) if isinstance(cover, dict) else 0,
            "cover_height": cover.get("height", 0) if isinstance(cover, dict) else 0,
            "note_type": note_card.get("type", item.get("type", "")),
        })

    # Sort by likes descending
    cards.sort(key=lambda c: c["likes"], reverse=True)

    # Step 4: Fetch detail for top posts (get full body text)
    top_n = min(10, len(cards))
    log(f"Fetching detail for top {top_n} posts...")

    detail_map = {}  # note_id -> detail dict
    for idx, card in enumerate(cards[:top_n]):
        note_id = card["note_id"]
        if not note_id:
            continue

        log(f"  [{idx+1}/{top_n}] reading {note_id}...")
        detail_raw = run_xhs(["read", note_id, "--json"], timeout=60)
        if not detail_raw:
            log(f"    Failed to read detail")
            continue

        try:
            detail = json.loads(detail_raw)
            note = detail.get("note", {})
            detail_map[note_id] = note
            body_len = len(note.get("desc", ""))
            log(f"    OK: body={body_len} chars, tags={len(note.get('tagList', []))}")
        except json.JSONDecodeError:
            log(f"    Failed to parse detail JSON")

    log(f"Detail fetched for {len(detail_map)}/{top_n} posts")

    # Step 5: Build results, merging detail where available
    results = []
    for card in cards[:limit]:
        note_id = card["note_id"]
        detail = detail_map.get(note_id, {})
        detail_interact = detail.get("interactInfo", {})

        # Detail data takes priority over search card data
        body = detail.get("desc", "")
        title = detail.get("title") or card["title"]
        text = body if body else title

        # Extract tags from detail
        tags = [t.get("name", "") for t in detail.get("tagList", []) if t.get("name")]

        # Timestamp from detail
        posted_at = ""
        ts = detail.get("time")
        if ts:
            from datetime import datetime, timezone
            posted_at = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")

        results.append({
            "source_platform": "xhs",
            "url": card["url"],
            "title": title,
            "text": text,
            "author": detail.get("user", {}).get("nickname") or card["author"],
            "author_followers": 0,
            "likes": parse_count(detail_interact.get("likedCount")) if detail_interact else card["likes"],
            "favorites": parse_count(detail_interact.get("collectedCount")) if detail_interact else card["favorites"],
            "comments": parse_count(detail_interact.get("commentCount")) if detail_interact else card["comments"],
            "shares": parse_count(detail_interact.get("shareCount")) if detail_interact else card["shares"],
            "posted_at": posted_at or card.get("published", ""),
            "keyword_matched": keyword,
            "engagement_score": 0,
            "content_hash": "",
            "tags": tags,
            "ip_location": detail.get("ipLocation", ""),
            "cover_url": card["cover_url"],
            "cover_width": card["cover_width"],
            "cover_height": card["cover_height"],
            "note_type": card["note_type"],
        })

    log(f"Found {len(results)} XHS posts for '{keyword}' ({len(detail_map)} with full detail)")
    return results


def main():
    parser = argparse.ArgumentParser(description="Search XHS via xhs-cli")
    parser.add_argument("--keyword", required=True, help="Search keyword")
    parser.add_argument("--limit", type=int, default=30, help="Max results")
    args = parser.parse_args()

    results = search_xhs(args.keyword, args.limit)
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
