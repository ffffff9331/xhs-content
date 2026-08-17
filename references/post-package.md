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
    "series": "护理考研"
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
- `approval_lock`: Added only after the user approves the exact final title, body, tags, and cover. Do not edit a locked package; create a new version and obtain fresh approval.
