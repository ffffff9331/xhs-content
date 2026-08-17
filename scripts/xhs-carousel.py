#!/usr/bin/env python3
"""Render Chinese XiaoHongShu carousel cards from a compact JSON plan."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
from pathlib import Path


WIDTH = 1080
HEIGHT = 1440
PALETTES = {
    "sage": {
        "ink": "#173035", "muted": "#597076", "accent": "#146C5A",
        "soft": "#CDEEE5", "softest": "#EDF8F4", "warm": "#FFE39A",
    },
    "coral": {
        "ink": "#15383A", "muted": "#587073", "accent": "#FF5A47",
        "soft": "#FFD7CF", "softest": "#FFF7F2", "warm": "#FFD35A",
    },
}
FONT = "PingFang SC, Hiragino Sans GB, Microsoft YaHei, Noto Sans CJK SC, sans-serif"


def escape(value: str) -> str:
    return html.escape(str(value), quote=True)


def text(x: int, y: int, value: str, size: int, *, fill: str, weight: int = 400, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(value)}</text>'
    )


def text_lines(x: int, y: int, values: list[str], size: int, line_height: int, *, fill: str, weight: int = 400) -> str:
    return "".join(text(x, y + index * line_height, value, size, fill=fill, weight=weight) for index, value in enumerate(values))


def dots(palette: dict[str, str]) -> str:
    return "".join(
        f'<circle cx="{866 + col * 24}" cy="{112 + row * 24}" r="4" fill="{palette["accent"]}" opacity="0.22"/>'
        for row in range(5) for col in range(6)
    )


def footer(index: int, series: str, palette: dict[str, str]) -> str:
    return (
        text(72, 1354, series, 24, fill=palette["muted"], weight=500)
        + text(1008, 1354, f"{index:02d}", 24, fill=palette["accent"], weight=700, anchor="end")
        + f'<line x1="72" y1="1381" x2="1008" y2="1381" stroke="#D8E6E1" stroke-width="3"/>'
    )


def badge(label: str, palette: dict[str, str]) -> str:
    width = max(164, len(label) * 34 + 58)
    return (
        f'<rect x="72" y="90" width="{width}" height="58" rx="29" fill="{palette["softest"]}"/>'
        + text(72 + width // 2, 129, label, 25, fill=palette["accent"], weight=650, anchor="middle")
    )


def cover(slide: dict, index: int, series: str, palette: dict[str, str]) -> str:
    title = slide.get("title", [])
    quote = slide.get("quote", [])
    illustration = f'''
      <g transform="translate(655 500)">
        <rect x="16" y="245" width="265" height="222" rx="30" fill="{palette["soft"]}"/>
        <rect x="56" y="84" width="198" height="150" rx="20" fill="{palette["ink"]}"/>
        <rect x="72" y="101" width="166" height="108" rx="12" fill="{palette["soft"]}"/>
        <rect x="104" y="234" width="101" height="20" rx="10" fill="{palette["ink"]}" opacity=".45"/>
        <rect x="71" y="438" width="151" height="155" rx="17" fill="#FFFFFF" transform="rotate(-9 71 438)"/>
        <line x1="96" y1="480" x2="194" y2="464" stroke="{palette["accent"]}" stroke-width="9" stroke-linecap="round"/>
        <line x1="100" y1="516" x2="181" y2="502" stroke="{palette["accent"]}" stroke-width="9" stroke-linecap="round" opacity=".55"/>
        <rect x="246" y="420" width="110" height="150" rx="20" fill="{palette["accent"]}"/>
        <rect x="263" y="440" width="77" height="30" rx="8" fill="{palette["warm"]}"/>
      </g>'''
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#F9FCFA"/>
  <rect width="{WIDTH}" height="28" fill="{palette["accent"]}"/>
  {badge(slide.get("badge", "图文笔记"), palette)}
  {dots(palette)}
  {text_lines(72, 330, title, 82, 105, fill=palette["ink"], weight=800)}
  {text(72, 594, slide.get("subtitle", ""), 34, fill=palette["muted"], weight=500)}
  {illustration}
  <rect x="72" y="960" width="936" height="238" rx="34" fill="{palette["accent"]}"/>
  {text_lines(116, 1032, quote, 43, 60, fill="#FFFFFF", weight=700)}
  {text(116, 1155, slide.get("small", ""), 26, fill="#FFFFFF", weight=500)}
  {footer(index, series, palette)}
</svg>'''


def list_card(slide: dict, index: int, series: str, palette: dict[str, str]) -> str:
    item_markup = []
    for item_index, item in enumerate(slide.get("items", [])[:3]):
        y = 535 + item_index * 162
        number_fill = palette["soft"] if item_index % 2 == 0 else palette["warm"]
        item_markup.extend([
            f'<circle cx="112" cy="{y - 12}" r="18" fill="{number_fill}"/>',
            text(112, y - 3, str(item_index + 1), 24, fill=palette["accent"], weight=700, anchor="middle"),
            text(158, y, item.get("heading", ""), 38, fill=palette["ink"], weight=650),
            text(158, y + 52, item.get("detail", ""), 32, fill=palette["muted"], weight=500),
        ])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect width="{WIDTH}" height="{HEIGHT}" fill="#F9FCFA"/>
  <rect width="{WIDTH}" height="28" fill="{palette["accent"]}"/>
  {badge(slide.get("badge", "重点"), palette)}
  {dots(palette)}
  {text_lines(72, 270, slide.get("title", []), 72, 85, fill=palette["ink"], weight=780)}
  {text(72, 415, slide.get("note", ""), 30, fill=palette["muted"], weight=500)}
  <rect x="72" y="462" width="936" height="784" rx="32" fill="#FFFFFF" stroke="#D8E6E1" stroke-width="3"/>
  {''.join(item_markup)}
  {footer(index, series, palette)}
</svg>'''


def svg_for_slide(slide: dict, index: int, series: str, palette: dict[str, str]) -> str:
    if slide.get("kind") == "cover":
        return cover(slide, index, series, palette)
    return list_card(slide, index, series, palette)


def convert_to_png(svg_path: Path) -> bool:
    png_path = svg_path.with_suffix(".png")
    if shutil.which("sips"):
        subprocess.run(["sips", "-s", "format", "png", str(svg_path), "--out", str(png_path)], check=True, capture_output=True)
        return True
    if shutil.which("magick"):
        subprocess.run(["magick", str(svg_path), str(png_path)], check=True, capture_output=True)
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a six-page XHS carousel from JSON.")
    parser.add_argument("--input", required=True, help="Carousel JSON file")
    parser.add_argument("--out-dir", required=True, help="Directory for SVG and PNG slides")
    args = parser.parse_args()

    plan = json.loads(Path(args.input).read_text(encoding="utf-8"))
    slides = plan.get("slides", [])
    if not 2 <= len(slides) <= 10:
        raise SystemExit("Carousel JSON must include 2 to 10 slides.")

    palette = PALETTES.get(plan.get("theme", "sage"), PALETTES["sage"])
    series = plan.get("series", "小红书图文")
    output = Path(args.out_dir)
    output.mkdir(parents=True, exist_ok=True)
    png_count = 0

    for index, slide in enumerate(slides, start=1):
        name = f"{index:02d}-{slide.get('slug', slide.get('kind', 'slide'))}.svg"
        svg_path = output / name
        svg_path.write_text(svg_for_slide(slide, index, series, palette), encoding="utf-8")
        png_count += int(convert_to_png(svg_path))

    print(f"Rendered {len(slides)} SVG slides to {output}")
    if png_count:
        print(f"Rendered {png_count} PNG slides alongside the SVGs")
    else:
        print("No PNG renderer found; use the SVGs directly or install sips/ImageMagick.")


if __name__ == "__main__":
    main()
