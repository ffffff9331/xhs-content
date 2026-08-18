# Post Package Schema

Use this JSON for every XHS image-note deliverable. It is the single source used to render the cover and publish the note.

```json
{
  "mode": "standard",
  "title": "🆘非典型考研人还有戏吗？",
  "body": "二本 + 二战 + 在职 + 30+，是不是已经把考研劝退四件套集齐了？\n\n先别急着自己淘汰自己。",
  "hashtags": ["护理考研", "二战考研", "在职考研", "30岁考研", "护理研究生"],
  "cover": {
    "style": "xhs-bold",
    "badge": "护理考研｜真实建议",
    "headline": ["二本 / 二战", "在职 / 30+"],
    "hook": "还能上岸吗？",
    "supporting": "先别自己把自己劝退！",
    "series": "护理考研",
    "palette": {
      "ink": "#152D4B",
      "muted": "#60728B",
      "accent": "#F05B4F",
      "soft": "#DDE8F4",
      "softest": "#F7FAFE",
      "warm": "#FFD36A"
    },
    "visual": {
      "layout": "photo-story",
      "subject": "晚间自习室里复习的护理考研人",
      "mood": "真实、克制、有一点顶住压力的力量",
      "required_elements": ["人物", "书桌", "学习场景", "左侧标题留白"],
      "text_safe_area": "left",
      "composition": "split-panel",
      "headline_treatment": "solid"
    },
    "scene": {
      "prompt": "真实手机纪实摄影。下班后的安静自习室，一位成年护理考研人坐在画面右侧的书桌前整理专业课笔记，桌上有摊开的护理教材、荧光笔和温暖台灯，左侧保持干净的深色留白。避免摆拍和科技感插画。",
      "negative_prompt": "任何文字、中文、数字、logo、水印、抽象电脑插画、无关人物、手部畸形、过度磨皮",
      "aspect_ratio": "3:4",
      "subject_visibility": "人物、书桌和护理学习资料在手机缩略图上都清楚可辨，主体位于右侧，不被标题遮住。"
    },
    "research": {
      "query": "在职考研 / 考研作息",
      "inspected_note_ids": ["note-id-1", "note-id-2", "note-id-3"],
      "patterns": {
        "composition": ["人物占画面右侧，左侧留给大字", "首屏只保留一个明确动作"],
        "typography": ["2 行短句大标题", "高对比结果贴纸"],
        "color": ["深色压住夜间学习场景", "用一个暖色结果块提亮"],
        "subject_treatment": ["真实书桌和学习资料可见", "不使用抽象电脑插画"]
      },
      "differentiation": "保留在职备考的夜间真实感，但使用全新的场景、标题和左侧文字安全区，不复用任何参考封面。"
    },
    "design": {
      "mode": "custom",
      "canvas_fill": "#F7FAFE",
      "image": {"x": 486, "y": 0, "width": 594, "height": 1440},
      "panels": [{"x": 0, "y": 0, "width": 650, "height": 1440, "fill": "#152D4B", "opacity": 0.9}],
      "badge": {"x": 72, "y": 84, "width": 304, "height": 56, "fill": "#F7FAFE", "text_fill": "#F05B4F"},
      "headline": {"x": 72, "y": 350, "size": 80, "line_height": 100, "fill": "#FFFFFF", "weight": 850},
      "hook": {"x": 72, "y": 945, "size": 48, "fill": "#FFD36A", "weight": 900},
      "supporting": {"x": 72, "y": 1010, "size": 30, "fill": "#DDE8F4", "weight": 650},
      "accent": {"x": 72, "y": 1080, "width": 160, "height": 8, "fill": "#F05B4F"},
      "footer": {"y": 1352, "fill": "#FFFFFF"}
    }
  },
  "publish": {
    "visibility": "public",
    "schedule": null
  }
}
```

- `mode`: `standard` or `short`.
- `title`: Exact XHS title. Do not repeat it inside `body`.
- `body`: The complete approved caption, excluding the final hashtag line.
- `hashtags`: Plain names without `#`.
- `cover.headline`: 2-3 tension-setting lines, never body paragraphs.
- `cover.style`: Always `xhs-bold`. This is a hard requirement for high-contrast, recognizable XHS hierarchy.
- `cover.hook`: Largest contrast line, normally a question or outcome.
- `cover.supporting`: Short reassurance, provocation, or next action.
- `cover.palette`: Six researched category colors (`ink`, `muted`, `accent`, `soft`, `softest`, `warm`) in `#RRGGBB` format. It overrides the renderer's fallback theme so unrelated categories do not share one palette.
- `cover.visual`: Required for all newly created covers. It is the art direction, not decorative metadata:
  - `layout`: `photo-story` for a subject-led scene, `photo-diary` for a personal/lifestyle memory, `product-focus` for a product/store/food/object/venue, `editorial` for career/education/interview/point-of-view content, or `checklist` for a true list/comparison cover.
  - `subject`: Name the literal subject a reader must see. For a kitten post, say `幼猫 + 安全居家环境`; for nursing study, say `护理考研人 + 自习室`; never write only an abstract mood.
  - `mood`: The emotional treatment of the visual.
  - `required_elements`: Concrete items that prove the cover belongs to this note.
  - `text_safe_area`: Where headline typography may sit without covering the subject.
  - `composition`: The actual cover structure chosen after research: `full-bleed`, `split-panel`, `framed-photo`, `lower-panel`, or `checklist-grid`. It must change the renderer, not remain a mood-only note.
  - `headline_treatment`: `solid`, `outline`, or `label`, selected from the category research rather than used uniformly.
- `cover.scene`: Required whenever the chosen cover is **scene-led** (`photo-story`, `photo-diary`, `product-focus`, or an `editorial` cover whose `design.image.visible` is not `false`). It turns the unique visual direction into a literal scene-image request. A research-backed, text-led editorial cover may set `design.image.visible` to `false` and omit this block:
  - `prompt`: The original scene, camera treatment, environment, subject action, lighting, and text-safe area. It must describe this particular post rather than a category template.
  - `negative_prompt`: At minimum excludes embedded text, Chinese characters, logos/watermarks, and unrelated subjects. Add topic-specific failures such as extra pets, wrong food, or generic office imagery when relevant.
  - `aspect_ratio`: Always `3:4`.
  - `subject_visibility`: Explains why the required elements remain recognisable at phone-thumbnail scale.
  - Run `python3 scripts/xhs-scene-prompt.py --input <post-package.json> --json`, generate **one new text-free image** with the available image-generation tool, save it as `publish/background.png`, and then pass that file to `xhs-cover.py --background`. Do not reuse a previous topic's scene image.
- `cover.design`: Required for newly created covers. It is an executable, post-specific visual blueprint rather than a preset name:
  - `mode`: Always `custom` for a new cover.
  - `canvas_fill`, `image`, `panels`, `badge`, `headline`, `hook`, `supporting`, `accent`, and `footer`: define the subject crop, text zones, contrast treatment, and hierarchy for this one note. Set `image.visible` to `false` only when current same-topic research clearly supports a text-led or illustration-led cover.
  - Do not duplicate a previous post's blueprint unless the actual topic, visual research, and source image legitimately demand the same result. Named `cover.visual.layout` values remain only as legacy fallbacks.
- Do not reuse a generic information-card illustration when the post needs a real visible subject. `photo-story` and `photo-diary` require a text-free, subject-relevant background passed to `xhs-cover.py --background`.
- `cover.research`: Required for every newly created cover after running `xhs-cover-research.py`. It proves the cover was informed by current high-engagement posts in the same category rather than a universal template:
  - `query`: Exact search terms used for this post.
  - `inspected_note_ids`: 3–8 note IDs represented in the private `cover-research/` output.
  - `patterns`: Lists of observed `composition`, `typography`, `color`, and `subject_treatment` patterns. Describe shared rules, never copy a specific creator.
  - `differentiation`: One sentence describing the new cover's original scene and layout decision.
- Reference images are private visual research only. Never include them in the publish folder, use them as background assets, or upload them to GitHub.
- `approval_lock`: Added only after the user approves the exact final title, body, tags, and cover. Do not edit a locked package; create a new version and obtain fresh approval.
