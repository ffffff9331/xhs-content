#!/usr/bin/env python3
"""Render one text-safe, XiaoHongShu-style cover from a post package."""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import mimetypes
from pathlib import Path


def load_carousel_renderer():
    source = Path(__file__).with_name("xhs-carousel.py")
    spec = importlib.util.spec_from_file_location("xhs_carousel", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load xhs-carousel.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description="Render one XHS cover from post-package.json.")
    parser.add_argument("--input", required=True, help="Path to post-package.json")
    parser.add_argument("--out-dir", required=True, help="Directory for cover.svg and cover.png")
    parser.add_argument("--theme", default="coral", choices=("sage", "coral"))
    parser.add_argument("--background", help="Optional text-free scene image behind the XHS typography")
    args = parser.parse_args()

    package = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cover = package.get("cover", {})
    if cover.get("style") != "xhs-bold":
        raise SystemExit("cover.style must be xhs-bold")
    headline = cover.get("headline", [])
    if not isinstance(headline, list) or not 2 <= len(headline) <= 3:
        raise SystemExit("cover.headline must contain 2 or 3 lines")
    if not cover.get("hook") or not cover.get("supporting"):
        raise SystemExit("cover.hook and cover.supporting are required")

    renderer = load_carousel_renderer()
    slide = {
        "kind": "cover",
        "badge": cover.get("badge", "小红书笔记"),
        "title": headline,
        "subtitle": cover["supporting"],
        "quote": [cover["hook"], cover["supporting"]],
        "small": cover.get("series", package.get("title", "")),
    }
    palette = renderer.PALETTES[args.theme]
    output = Path(args.out_dir)
    output.mkdir(parents=True, exist_ok=True)
    svg_path = output / "cover.svg"
    svg = renderer.cover(slide, 1, cover.get("series", "小红书图文"), palette)
    if args.background:
        background = Path(args.background).resolve()
        if not background.is_file():
            raise SystemExit(f"Background does not exist: {background}")
        mime = mimetypes.guess_type(background.name)[0] or "image/png"
        encoded = base64.b64encode(background.read_bytes()).decode("ascii")
        layer = (
            f'<image href="data:{mime};base64,{encoded}" width="1080" height="1440" '
            'preserveAspectRatio="xMidYMid slice" opacity="0.42"/>'
            f'<rect width="1080" height="1440" fill="{palette["softest"]}" opacity="0.62"/>'
        )
        original_background = '<rect width="1080" height="1440" fill="#F9FCFA"/>'
        if original_background not in svg:
            raise RuntimeError("Could not place the optional background image in the cover template")
        svg = svg.replace(original_background, layer, 1)
    svg_path.write_text(svg, encoding="utf-8")
    converted = renderer.convert_to_png(svg_path)
    print(f"Rendered {svg_path}")
    if converted:
        print(f"Rendered {svg_path.with_suffix('.png')}")


if __name__ == "__main__":
    main()
