#!/usr/bin/env python3
"""Render one text-safe, XiaoHongShu-style cover from a post package."""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import mimetypes
import re
from pathlib import Path


def load_carousel_renderer():
    source = Path(__file__).with_name("xhs-carousel.py")
    spec = importlib.util.spec_from_file_location("xhs_carousel", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load xhs-carousel.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def image_data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def resolve_palette(cover: dict, base_palette: dict[str, str]) -> dict[str, str]:
    """Allow a researched category palette while retaining the built-in theme fallback."""
    palette = dict(base_palette)
    custom = cover.get("palette")
    if custom is None:
        return palette
    if not isinstance(custom, dict):
        raise SystemExit("cover.palette must be an object of hex colors")
    for key in ("ink", "muted", "accent", "soft", "softest", "warm"):
        value = custom.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            raise SystemExit(f"cover.palette.{key} must be a six-digit hex color")
        palette[key] = value.upper()
    return palette


def photo_story_cover(slide: dict, index: int, series: str, palette: dict[str, str], background: Path, renderer) -> str:
    """Render a subject-led cover with the scene as the primary visual."""
    image = image_data_uri(background)
    title = slide.get("title", [])
    hook = slide.get("quote", [""])[0]
    supporting = slide.get("subtitle", "")
    badge_label = slide.get("badge", "图文笔记")
    badge_width = max(244, len(str(badge_label)) * 28 + 66)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440">
  <image href="{image}" width="1080" height="1440" preserveAspectRatio="xMidYMid slice"/>
  <rect width="1080" height="1440" fill="#0E3033" opacity="0.20"/>
  <rect x="0" y="0" width="670" height="1440" fill="#133B3D" opacity="0.88"/>
  <rect x="0" y="0" width="1080" height="26" fill="{palette["accent"]}"/>
  <rect x="72" y="88" width="{badge_width}" height="56" rx="28" fill="#FFF7F2"/>
  {renderer.text(72 + badge_width // 2, 126, badge_label, 24, fill=palette["accent"], weight=700, anchor="middle")}
  {renderer.text_lines(72, 332, title, 78, 102, fill="#FFFFFF", weight=800)}
  <rect x="72" y="846" width="540" height="170" rx="26" fill="{palette["accent"]}"/>
  {renderer.text(106, 920, hook, 43, fill="#FFFFFF", weight=800)}
  {renderer.text(106, 978, supporting, 30, fill="#FFFFFF", weight=600)}
  <rect x="72" y="1098" width="294" height="54" rx="27" fill="#FFFFFF" opacity="0.94"/>
  {renderer.text(219, 1134, slide.get("visual_label", "图文攻略"), 22, fill=palette["ink"], weight=650, anchor="middle")}
  {renderer.text(72, 1352, series, 24, fill="#FFFFFF", weight=600)}
  {renderer.text(1008, 1352, f"{index:02d}", 24, fill="#FFFFFF", weight=700, anchor="end")}
</svg>'''


def photo_diary_cover(slide: dict, index: int, series: str, palette: dict[str, str], background: Path, renderer) -> str:
    """Render a warmer, diary-style cover for lifestyle or personal-story posts."""
    image = image_data_uri(background)
    title = slide.get("title", [])
    hook = slide.get("quote", [""])[0]
    badge_label = slide.get("badge", "图文笔记")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440">
  <rect width="1080" height="1440" fill="#FFF8F3"/>
  <rect width="1080" height="26" fill="{palette["accent"]}"/>
  <rect x="62" y="214" width="956" height="792" rx="34" fill="#FFFFFF" transform="rotate(-2 540 610)"/>
  <image href="{image}" x="86" y="238" width="908" height="744" preserveAspectRatio="xMidYMid slice"/>
  <rect x="72" y="82" width="302" height="56" rx="28" fill="{palette["soft"]}"/>
  {renderer.text(223, 120, badge_label, 24, fill=palette["accent"], weight=700, anchor="middle")}
  <rect x="72" y="1038" width="936" height="252" rx="32" fill="#FFFFFF"/>
  {renderer.text_lines(112, 1122, title, 68, 84, fill=palette["ink"], weight=800)}
  <rect x="670" y="1137" width="282" height="82" rx="22" fill="{palette["accent"]}" transform="rotate(-3 811 1178)"/>
  {renderer.text(811, 1190, hook, 29, fill="#FFFFFF", weight=800, anchor="middle")}
  {renderer.text(72, 1352, series, 24, fill=palette["muted"], weight=600)}
  {renderer.text(1008, 1352, f"{index:02d}", 24, fill=palette["accent"], weight=700, anchor="end")}
</svg>'''


def product_focus_cover(slide: dict, index: int, series: str, palette: dict[str, str], background: Path, renderer) -> str:
    """Render a product, venue, or object-led cover without hiding the thing being reviewed."""
    image = image_data_uri(background)
    title = slide.get("title", [])
    hook = slide.get("quote", [""])[0]
    supporting = slide.get("subtitle", "")
    badge_label = slide.get("badge", "图文笔记")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440">
  <rect width="1080" height="1440" fill="#FFF8F2"/>
  <rect width="1080" height="26" fill="{palette["accent"]}"/>
  <rect x="72" y="82" width="330" height="56" rx="28" fill="{palette["soft"]}"/>
  {renderer.text(237, 120, badge_label, 24, fill=palette["accent"], weight=700, anchor="middle")}
  <rect x="72" y="198" width="936" height="690" rx="34" fill="#FFFFFF"/>
  <image href="{image}" x="92" y="218" width="896" height="650" preserveAspectRatio="xMidYMid slice"/>
  <rect x="716" y="804" width="240" height="92" rx="24" fill="{palette["accent"]}" transform="rotate(-4 836 850)"/>
  {renderer.text(836, 863, hook, 30, fill="#FFFFFF", weight=800, anchor="middle")}
  {renderer.text_lines(72, 1010, title, 70, 86, fill=palette["ink"], weight=800)}
  {renderer.text(72, 1218, supporting, 31, fill=palette["muted"], weight=600)}
  {renderer.text(72, 1352, series, 24, fill=palette["muted"], weight=600)}
  {renderer.text(1008, 1352, f"{index:02d}", 24, fill=palette["accent"], weight=700, anchor="end")}
</svg>'''


def editorial_cover(slide: dict, index: int, series: str, palette: dict[str, str], background: Path, renderer) -> str:
    """Render a bolder cover for careers, education, interviews, and point-of-view posts."""
    image = image_data_uri(background)
    title = slide.get("title", [])
    hook = slide.get("quote", [""])[0]
    supporting = slide.get("subtitle", "")
    badge_label = slide.get("badge", "图文笔记")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440">
  <image href="{image}" width="1080" height="1440" preserveAspectRatio="xMidYMid slice"/>
  <rect width="1080" height="1440" fill="#0B2022" opacity="0.32"/>
  <rect x="0" y="786" width="1080" height="654" fill="#113538" opacity="0.94"/>
  <rect x="0" y="0" width="1080" height="26" fill="{palette["accent"]}"/>
  <rect x="72" y="84" width="330" height="56" rx="28" fill="#FFFFFF" opacity="0.95"/>
  {renderer.text(237, 121, badge_label, 24, fill=palette["accent"], weight=700, anchor="middle")}
  {renderer.text_lines(72, 938, title, 76, 94, fill="#FFFFFF", weight=800)}
  <rect x="72" y="1160" width="510" height="72" rx="20" fill="{palette["accent"]}"/>
  {renderer.text(106, 1209, hook, 32, fill="#FFFFFF", weight=800)}
  {renderer.text(72, 1289, supporting, 28, fill="#D9F0EC", weight=600)}
  {renderer.text(72, 1352, series, 24, fill="#FFFFFF", weight=600)}
  {renderer.text(1008, 1352, f"{index:02d}", 24, fill="#FFFFFF", weight=700, anchor="end")}
</svg>'''


def full_bleed_cover(
    slide: dict,
    index: int,
    series: str,
    palette: dict[str, str],
    background: Path,
    renderer,
    headline_treatment: str,
) -> str:
    """Use a scene-first, immersive cover when the researched category calls for it."""
    image = image_data_uri(background)
    title = slide.get("title", [])
    hook = slide.get("quote", [""])[0]
    supporting = slide.get("subtitle", "")
    badge_label = slide.get("badge", "图文笔记")
    badge_width = max(244, len(str(badge_label)) * 28 + 66)
    title_y = 900 if len(title) == 2 else 818
    title_lines = []
    for position, line in enumerate(title):
        y = title_y + position * 104
        if headline_treatment == "outline":
            title_lines.append(
                f'<text x="72" y="{y}" font-family="{renderer.FONT}" font-size="84" font-weight="900" '
                f'fill="#FFFFFF" stroke="{palette["ink"]}" stroke-width="10" paint-order="stroke">'
                f'{renderer.escape(line)}</text>'
            )
        else:
            title_lines.append(renderer.text(72, y, line, 84, fill="#FFFFFF", weight=850))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440">
  <image href="{image}" width="1080" height="1440" preserveAspectRatio="xMidYMid slice"/>
  <rect width="1080" height="1440" fill="{palette["ink"]}" opacity="0.18"/>
  <rect x="0" y="732" width="1080" height="708" fill="{palette["ink"]}" opacity="0.84"/>
  <rect x="0" y="0" width="1080" height="24" fill="{palette["accent"]}"/>
  <rect x="72" y="84" width="{badge_width}" height="56" rx="28" fill="{palette["warm"]}"/>
  {renderer.text(72 + badge_width // 2, 121, badge_label, 24, fill=palette["ink"], weight=800, anchor="middle")}
  {''.join(title_lines)}
  {renderer.text(72, 1166, hook, 50, fill=palette["warm"], weight=900)}
  {renderer.text(72, 1232, supporting, 29, fill="#FFFFFF", weight=650)}
  <rect x="72" y="1282" width="170" height="8" rx="4" fill="{palette["accent"]}"/>
  {renderer.text(72, 1352, series, 24, fill="#FFFFFF", weight=600)}
  {renderer.text(1008, 1352, f"{index:02d}", 24, fill="#FFFFFF", weight=700, anchor="end")}
</svg>'''


def custom_cover(slide: dict, index: int, series: str, palette: dict[str, str], background, design: dict, renderer) -> str:
    """Render a per-post visual blueprint instead of selecting a named template."""
    def number(value: object, fallback: int) -> int:
        return int(value) if isinstance(value, (int, float)) else fallback

    def color(value: object, fallback: str) -> str:
        return str(value) if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value) else fallback

    def opacity(value: object, fallback: float) -> float:
        return float(value) if isinstance(value, (int, float)) and 0 <= float(value) <= 1 else fallback

    def is_visible(spec: dict, fallback: bool = True) -> bool:
        return spec.get("visible", fallback) is not False

    canvas = color(design.get("canvas_fill"), palette["softest"])
    image_box = design.get("image", {}) if isinstance(design.get("image"), dict) else {}
    image_visible = image_box.get("visible", True) is not False and background is not None
    image_x = number(image_box.get("x"), 0)
    image_y = number(image_box.get("y"), 0)
    image_width = number(image_box.get("width"), 1080)
    image_height = number(image_box.get("height"), 1440)
    image_opacity = opacity(image_box.get("opacity"), 1)

    panel_markup = []
    for panel in design.get("panels", []) if isinstance(design.get("panels", []), list) else []:
        if not isinstance(panel, dict):
            continue
        panel_markup.append(
            f'<rect x="{number(panel.get("x"), 0)}" y="{number(panel.get("y"), 0)}" '
            f'width="{number(panel.get("width"), 1080)}" height="{number(panel.get("height"), 1440)}" '
            f'rx="{number(panel.get("radius"), 0)}" fill="{color(panel.get("fill"), palette["ink"])}" '
            f'opacity="{opacity(panel.get("opacity"), 1)}"/>'
        )

    badge = design.get("badge", {}) if isinstance(design.get("badge"), dict) else {}
    badge_x = number(badge.get("x"), 72)
    badge_y = number(badge.get("y"), 84)
    badge_width = number(badge.get("width"), max(244, len(str(slide.get("badge", "图文笔记"))) * 28 + 66))
    badge_height = number(badge.get("height"), 56)
    badge_fill = color(badge.get("fill"), palette["softest"])
    badge_text = color(badge.get("text_fill"), palette["accent"])

    headline = design.get("headline", {}) if isinstance(design.get("headline"), dict) else {}
    headline_x = number(headline.get("x"), 72)
    headline_y = number(headline.get("y"), 920)
    headline_size = number(headline.get("size"), 78)
    headline_height = number(headline.get("line_height"), 96)
    headline_fill = color(headline.get("fill"), "#FFFFFF")
    headline_weight = number(headline.get("weight"), 850)
    headline_stroke = color(headline.get("stroke"), "")
    headline_stroke_width = number(headline.get("stroke_width"), 0)
    headline_shadow = color(headline.get("shadow_fill"), "")
    headline_shadow_x = number(headline.get("shadow_x"), 4)
    headline_shadow_y = number(headline.get("shadow_y"), 4)
    headline_parts = []
    for position, line in enumerate(slide.get("title", [])):
        y = headline_y + position * headline_height
        if headline_shadow:
            headline_parts.append(
                renderer.text(headline_x + headline_shadow_x, y + headline_shadow_y, line, headline_size, fill=headline_shadow, weight=headline_weight)
            )
        if headline_stroke and headline_stroke_width:
            headline_parts.append(
                f'<text x="{headline_x}" y="{y}" font-family="{renderer.FONT}" font-size="{headline_size}" '
                f'font-weight="{headline_weight}" fill="{headline_fill}" stroke="{headline_stroke}" '
                f'stroke-width="{headline_stroke_width}" paint-order="stroke">{renderer.escape(line)}</text>'
            )
        else:
            headline_parts.append(renderer.text(headline_x, y, line, headline_size, fill=headline_fill, weight=headline_weight))

    hook = design.get("hook", {}) if isinstance(design.get("hook"), dict) else {}
    support = design.get("supporting", {}) if isinstance(design.get("supporting"), dict) else {}
    footer = design.get("footer", {}) if isinstance(design.get("footer"), dict) else {}
    accent = design.get("accent", {}) if isinstance(design.get("accent"), dict) else {}
    hook_markup = renderer.text(
        number(hook.get("x"), 72),
        number(hook.get("y"), 1160),
        slide.get("quote", [""])[0],
        number(hook.get("size"), 48),
        fill=color(hook.get("fill"), palette["accent"]),
        weight=number(hook.get("weight"), 850),
    ) if is_visible(hook) else ""
    supporting_markup = renderer.text(
        number(support.get("x"), 72),
        number(support.get("y"), 1230),
        slide.get("subtitle", ""),
        number(support.get("size"), 30),
        fill=color(support.get("fill"), palette["muted"]),
        weight=number(support.get("weight"), 650),
    ) if is_visible(support) else ""
    accent_markup = ""
    if accent and is_visible(accent):
        accent_markup = (
            f'<rect x="{number(accent.get("x"), 72)}" y="{number(accent.get("y"), 1280)}" '
            f'width="{number(accent.get("width"), 170)}" height="{number(accent.get("height"), 8)}" '
            f'rx="{number(accent.get("radius"), 4)}" fill="{color(accent.get("fill"), palette["accent"])}"/>'
        )
    footer_y = number(footer.get("y"), 1352)
    footer_fill = color(footer.get("fill"), palette["muted"])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440">
  <rect width="1080" height="1440" fill="{canvas}"/>
  {f'<image href="{image_data_uri(background)}" x="{image_x}" y="{image_y}" width="{image_width}" height="{image_height}" preserveAspectRatio="xMidYMid slice" opacity="{image_opacity}"/>' if image_visible else ''}
  {''.join(panel_markup)}
  {f'<rect x="{badge_x}" y="{badge_y}" width="{badge_width}" height="{badge_height}" rx="{badge_height // 2}" fill="{badge_fill}"/>' if is_visible(badge) else ''}
  {renderer.text(badge_x + badge_width // 2, badge_y + 38, slide.get("badge", "图文笔记"), 24, fill=badge_text, weight=800, anchor="middle") if is_visible(badge) else ''}
  {''.join(headline_parts)}
  {hook_markup}
  {supporting_markup}
  {accent_markup}
  {renderer.text(72, footer_y, series, 24, fill=footer_fill, weight=600) if is_visible(footer) else ''}
  {renderer.text(1008, footer_y, f"{index:02d}", 24, fill=footer_fill, weight=700, anchor="end") if is_visible(footer) else ''}
</svg>'''


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
    visual = cover.get("visual", {}) if isinstance(cover.get("visual", {}), dict) else {}
    design = cover.get("design", {}) if isinstance(cover.get("design", {}), dict) else {}
    layout = visual.get("layout", "auto")
    composition = visual.get("composition", "")
    slide = {
        "kind": "cover",
        "badge": cover.get("badge", "小红书笔记"),
        "title": headline,
        "subtitle": cover["supporting"],
        "quote": [cover["hook"], cover["supporting"]],
        "small": cover.get("series", package.get("title", "")),
        "visual_label": visual.get("context_label", cover.get("series", "图文攻略")),
    }
    palette = resolve_palette(cover, renderer.PALETTES[args.theme])
    output = Path(args.out_dir)
    output.mkdir(parents=True, exist_ok=True)
    svg_path = output / "cover.svg"
    background = Path(args.background).resolve() if args.background else None
    if background and not background.is_file():
        raise SystemExit(f"Background does not exist: {background}")

    if layout == "auto":
        layout = "photo-story" if background else "checklist"
    photo_layouts = {"photo-story", "photo-diary", "product-focus", "editorial"}
    image_design = design.get("image", {}) if isinstance(design.get("image"), dict) else {}
    uses_subject_scene = image_design.get("visible", True) is not False
    if layout in photo_layouts and uses_subject_scene and not background:
        raise SystemExit(
            f"cover.visual.layout '{layout}' uses a subject scene and requires --background with a text-free, subject-relevant image"
        )

    if design.get("mode") == "custom":
        svg = custom_cover(slide, 1, cover.get("series", "小红书图文"), palette, background, design, renderer)
    elif composition == "full-bleed":
        if not background:
            raise SystemExit("cover.visual.composition 'full-bleed' requires --background")
        svg = full_bleed_cover(
            slide,
            1,
            cover.get("series", "小红书图文"),
            palette,
            background,
            renderer,
            visual.get("headline_treatment", "solid"),
        )
    elif layout == "photo-story":
        svg = photo_story_cover(slide, 1, cover.get("series", "小红书图文"), palette, background, renderer)
    elif layout == "photo-diary":
        svg = photo_diary_cover(slide, 1, cover.get("series", "小红书图文"), palette, background, renderer)
    elif layout == "product-focus":
        svg = product_focus_cover(slide, 1, cover.get("series", "小红书图文"), palette, background, renderer)
    elif layout == "editorial":
        svg = editorial_cover(slide, 1, cover.get("series", "小红书图文"), palette, background, renderer)
    elif layout == "checklist":
        svg = renderer.cover(slide, 1, cover.get("series", "小红书图文"), palette)
    else:
        raise SystemExit("cover.visual.layout must be auto, photo-story, photo-diary, product-focus, editorial, or checklist")

    if background and layout == "checklist":
        layer = (
            f'<image href="{image_data_uri(background)}" width="1080" height="1440" '
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
