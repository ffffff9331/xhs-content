#!/usr/bin/env python3
"""Publish an approved XHS image note using the current creator-page controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import site
import sys
from pathlib import Path


def load_xhs_cli():
    """Import xhs-cli whether it was installed by pipx, uv tool, or pip."""
    try:
        from xhs_cli.auth import cookie_str_to_dict, get_saved_cookie_string
        from xhs_cli.client import XhsClient
        return cookie_str_to_dict, get_saved_cookie_string, XhsClient
    except ModuleNotFoundError:
        binary = shutil.which("xhs")
        if binary:
            first_line = Path(binary).read_text(encoding="utf-8", errors="ignore").splitlines()[0:1]
            if first_line and first_line[0].startswith("#!"):
                executable = Path(first_line[0][2:])
                for candidate in executable.parent.parent.glob("lib/python*/site-packages"):
                    site.addsitedir(str(candidate))
        try:
            from xhs_cli.auth import cookie_str_to_dict, get_saved_cookie_string
            from xhs_cli.client import XhsClient
            return cookie_str_to_dict, get_saved_cookie_string, XhsClient
        except ModuleNotFoundError as error:
            raise SystemExit("xhs-cli Python package not found. Install it with: uv tool install xhs-cli") from error


PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish"
TITLE_SELECTOR = 'input[placeholder="填写标题会有更多赞哦"]'
EDITOR_SELECTOR = '[contenteditable="true"]'
PUBLISH_HOST_SELECTOR = 'xhs-publish-btn[is-publish="true"]'
AUTOMATION_RISK_NOTICE = (
    "AUTOMATION RISK: This command programmatically publishes to Xiaohongshu. "
    "Automated posting can trigger account risk controls or account penalties and is not the recommended workflow. "
    "Prefer manual upload in the creator page. Do not use this command for unattended, scheduled, bulk, or multi-account posting."
)


def full_caption(package: dict) -> str:
    body = str(package["body"]).strip()
    tags = package.get("hashtags", [])
    return body + ("\n\n" + " ".join(f"#{tag}" for tag in tags) if tags else "")


def digest(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def verify_final_version(package: dict, cover: Path) -> None:
    lock = package.get("approval_lock")
    expected = {
        "title_sha256": digest(str(package["title"]).strip()),
        "caption_sha256": digest(full_caption(package)),
        "cover_sha256": digest(cover.read_bytes()),
    }
    if lock != expected:
        raise RuntimeError(
            "The package is not locked to the exact final title, full caption, tags, and cover. "
            "Run xhs-style-check.py --write-lock only after user approval."
        )


def switch_to_image_note(page) -> None:
    # The creator page has changed tab class names several times. Match the
    # visible, exact tab label instead of coupling publication to one class.
    switched = page.evaluate("""() => {
        const visible = el => {
            const rect = el.getBoundingClientRect();
            const style = getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 &&
                style.visibility !== 'hidden' && style.display !== 'none';
        };
        const candidates = Array.from(document.querySelectorAll('*'))
            .filter(el => visible(el) && (el.innerText || '').trim() === '上传图文')
            .sort((left, right) => left.children.length - right.children.length);
        const imageTab = candidates[0];
        if (!imageTab) return false;
        imageTab.click();
        return true;
    }""")
    if not switched:
        raise RuntimeError("Could not find the creator page's 上传图文 tab")
    page.wait_for_timeout(2500)


def click_current_publish_control(page) -> None:
    """Click the red action inside the creator page's closed custom component.

    New creator pages expose no ordinary text button. The footer host is
    `xhs-publish-btn`; the red action is right of its save-draft action.
    Its position tracks the host width, which is more reliable than old
    `button:has-text('发布')` selectors.
    """
    host = page.query_selector(PUBLISH_HOST_SELECTOR)
    if not host:
        raise RuntimeError("Could not find the current xhs-publish-btn control")
    if host.get_attribute("submit-disabled") == "true":
        raise RuntimeError("The publish control is disabled")
    box = host.bounding_box()
    if not box:
        raise RuntimeError("The publish control is not visible")
    page.mouse.click(box["x"] + box["width"] / 2 + 72, box["y"] + box["height"] / 2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish an approved XHS image note.")
    parser.add_argument("--input", required=True, help="Approved post-package.json")
    parser.add_argument("--cover", required=True, help="Rendered PNG/JPG cover")
    parser.add_argument("--publish", action="store_true", help="Required to perform the external publication")
    parser.add_argument(
        "--acknowledge-automation-risk",
        action="store_true",
        help="Required acknowledgement that automated publishing carries account-risk and penalty risk",
    )
    parser.add_argument("--debug-screenshot", help="Optional screenshot path after the action")
    args = parser.parse_args()
    if not args.publish:
        raise SystemExit("Refusing to publish without --publish")
    if not args.acknowledge_automation_risk:
        raise SystemExit(
            f"{AUTOMATION_RISK_NOTICE}\n\n"
            "Refusing to continue. Upload manually, or pass --acknowledge-automation-risk only after the user explicitly accepts this risk."
        )
    print(AUTOMATION_RISK_NOTICE, file=sys.stderr, flush=True)

    cookie_str_to_dict, get_saved_cookie_string, XhsClient = load_xhs_cli()

    package = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cover = Path(args.cover).resolve()
    if not cover.is_file():
        raise SystemExit(f"Cover does not exist: {cover}")
    verify_final_version(package, cover)
    cookie = get_saved_cookie_string()
    if not cookie:
        raise SystemExit("No saved XHS session. Run xhs login first.")

    with XhsClient(cookie_str_to_dict(cookie)) as client:
        client._goto(PUBLISH_URL, timeout=30000, wait_min=4, wait_max=5, context="opening XHS creator page")
        page = client._page
        switch_to_image_note(page)
        file_inputs = page.query_selector_all('input[type="file"]')
        image_input = next(
            (item for item in file_inputs if "image" in (item.get_attribute("accept") or "").lower()),
            file_inputs[0] if file_inputs else None,
        )
        if not image_input:
            raise RuntimeError("Could not find the image-note upload input")
        image_input.set_input_files(str(cover))
        page.wait_for_timeout(6000)

        title = page.query_selector(TITLE_SELECTOR)
        editor = page.query_selector(EDITOR_SELECTOR)
        if not title or not editor:
            raise RuntimeError("Current creator-page title or caption selector was not found")
        title.fill(str(package["title"]).strip())
        editor.click()
        page.keyboard.type(full_caption(package))
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

        click_current_publish_control(page)
        page.wait_for_timeout(12000)
        if args.debug_screenshot:
            page.screenshot(path=str(Path(args.debug_screenshot).resolve()), full_page=True)

        body = page.text_content("body") or ""
        success = "published=true" in page.url or any(marker in body for marker in ("发布成功", "已发布", "审核中"))
        print(json.dumps({"published": success, "url": page.url}, ensure_ascii=False))
        if not success:
            raise SystemExit("Publish did not return an explicit success state")


if __name__ == "__main__":
    main()
