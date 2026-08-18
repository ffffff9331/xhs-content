# xhs-content

一个面向 Codex / OpenClaw 的小红书内容创作 Skill：从选题调研，到极具小红书风格的文案与封面，再到锁定最终版本并发布图文笔记。

它不是“写一篇文章，再随手配张海报”。每次完整创作都以同一个 `post-package.json` 为准，确保文案、封面、标签和发布内容始终是同一版。

[English](./README.en.md) | **中文**

## 能做什么

| 能力 | 结果 |
| --- | --- |
| 选题调研 | 搜索小红书热门内容，输出热度、常见钩子、评论问题、差异化角度与来源表 |
| 小红书文案 | 有情绪钩子、短段落、可执行建议和评论区互动收尾，不生成泛泛的公众号文章 |
| 一张强封面 | 默认生成一张 3:4 竖版封面：大字钩子、醒目对比、小标签和手机端可读的层级 |
| 封面赛道调研 | 每次出封面前检索同主题高互动笔记，生成私有参考墙，拆解构图、字数、色彩和主体呈现后再原创出图 |
| 内容感知封面 | 先写明画面主体、情绪、关键元素和文字安全区；幼猫内容必须看见幼猫，产品内容必须看见产品，不能套无关模板 |
| 场景配图 | 每篇照片型封面先生成专属的无文字场景图提示，再用 AI 或授权图生成主体相关的新底图，最后叠加稳定的中文标题排版 |
| 轮播图 | 需要清单、步骤或拆解时，生成 2–10 页图文轮播 |
| 最终版本锁定 | 对标题、完整文案（含标签）和封面生成哈希锁，阻止误把缩短预览版发出去 |
| 小红书发布 | 适配新版创作页的“上传图文”入口和发布按钮，只发布已锁定的最终版本 |

## 最重要的创作规则

这个 Skill 会把以下要求当成硬规则，而不是可有可无的建议：

- **文案必须有鲜明小红书感**：前 1–3 行就给钩子，像和朋友聊天，短段落，给出真实判断或可执行动作，最后明确引导评论。
- **封面必须有鲜明小红书感**：3:4 竖版、手机端一眼可读的主视觉与文字层级。原始探店实拍可能只需要两行压图大字，清单内容才需要标签和结果钩子；每个赛道从调研中选择自己的高对比色组，拒绝灰扑扑的 PPT 画风。
- **每次封面先做同赛道调研**：用当前主题检索小红书高互动笔记，保存仅供本地查看的封面参考墙，实际分析构图、标题密度、色彩、主体占比与标签位置。最终封面只借鉴赛道规律，必须使用全新的场景、文案和构图，不能复用参考图、抄标题或模仿某个作者的识别性设计。
- **不从固定模板库选封面**：新封面必须提交一份 `cover.design` 视觉蓝图，直接定义这篇内容的图片裁切、文字落点、遮罩、强调元素和页脚，而不是从“宠物版 / 火锅版 / 职场版”里挑一个。旧版式只保留给历史内容兼容。
- **封面必须和内容是同一个世界**：新建笔记要先有 `cover.visual` 视觉策划。人物、宠物和场景故事用 `photo-story`，生活记录用 `photo-diary`，产品/门店/食物/旅行对象用 `product-focus`，职场/教育/采访/观点用 `editorial`，只有清单/对比/流程内容才能使用 `checklist`。不同行业不能套同一张无关模板。
- **每张照片型封面都要换真正的底图**：`cover.scene` 必须写清本篇的镜头、环境、动作、主体、光线和文字安全区，并排除文字、中文、logo、水印及题材无关元素；它会生成可直接交给图片生成能力的提示。宠物、火锅店、职场、护理等内容要从源图开始就不一样，不能只换标题或换色。
- **默认交付“完整文案 + 一张封面”**。只有用户明确说“只要文字”时，才不生成封面。
- **完整文案永远优先于摘要**。用户确认过的正文不会被静默缩短；如需短版，会作为单独的 `mode: "short"` 包处理。
- **发布前必须锁定**。发布器会核对标题、完整正文（包括 hashtags）和封面；任一项变动都会拒绝发布，直到重新确认与锁定。

## 安装

### Codex

将本仓库放入 Codex 的 skills 目录：

```bash
git clone https://github.com/ffffff9331/xhs-content.git ~/.codex/skills/xhs-content
```

重启或刷新 Codex 后，可直接说：

```text
用 xhs-content 做一篇「二本、二战、在职、30 岁再考」的护理考研小红书笔记，要完整文案和一张封面。
```

### OpenClaw

支持 Git 安装的 OpenClaw 环境可使用：

```bash
openclaw skills install git:ffffff9331/xhs-content@main
```

安装后直接在对话中调用 `xhs-content`，或让助手按本 Skill 的工作流执行。

## 常见用法

### 1. 调研再创作

```text
查找护理读研相关的小红书热门内容，给我一份趋势报告；再做一篇“读完护理硕士仍进医院，三年到底换来了什么？”的笔记和一张封面。
```

调研输出会存入：

```text
data/<日期>-<关键词>/
├── sources.jsonl
├── report.md
├── drafts.md
├── cover-research/
│   ├── cover-references.json
│   ├── cover-reference-wall.html
│   ├── cover-reference-sheet.jpg
│   └── reference-covers/
└── post-package.json
```

涉及招生、学费、政策、医疗、薪资和就业等事实性内容时，应该优先核验官方来源。

### 2. 只做一篇图文笔记

```text
做一篇小红书笔记：二本、二战、在职、30 岁再考，分别该怎么评估风险和节奏？
文案和封面都要有极其鲜明的小红书风格，封面只要一张。
```

默认交付内容：

- 标题
- 完整正文和话题标签
- `post-package.json`
- `publish/cover.png`

在生成 `publish/cover.png` 前，Skill 会先运行同赛道封面调研。例如“幼猫到家”会同时检索 `幼猫到家` 和 `接猫清单`，查看当前高互动封面的视觉规律，再决定是用照片日记、实物焦点还是清单信息结构。调研参考只留在本地 `cover-research/`，不会被发布、不会作为封面底图、也不应提交到仓库。

调研后不会再机械套用某个“版式名称”。Skill 会生成本次专属的 `cover.design` 蓝图：背景在画布中的位置和裁切、需要哪些对比层、标题落在哪个区域、强调句怎样出现、页脚怎样收束，都由本篇主题与参考结论决定，并由校验器强制要求。

### 3. 用 AI 场景图做封面底图

```text
生成一张无文字的护理考研自习室场景图，并把它做成小红书封面底图。
```

场景图需要**没有任何嵌入文字或中文**，且画面要真的看得见本篇主体；标题和排版由封面渲染器统一完成，避免乱码和不可控字体。

照片型封面会先从 `post-package.json` 导出本篇专属的出图提示：

```bash
python3 scripts/xhs-scene-prompt.py --input data/<日期>-<关键词>/post-package.json --json
```

将其交给可用的图片生成能力，保存为 `publish/background.png`，再用 `xhs-cover.py --background` 合成最终封面。不同选题必须生成不同背景图，不能从固定模板库取图。

### 4. 制作轮播图

```text
把“护理读研账本：学费、补贴、机会成本和不能量化的回报”做成 6 页小红书轮播图。
```

轮播图适合步骤、清单和比较；首图仍必须通过封面风格检查。

### 5. 发布最终确认版

当用户已经明确确认标题、**完整文案**、标签、封面、可见范围和发布时间后：

```bash
python3 scripts/xhs-style-check.py \
  --input data/<日期>-<关键词>/post-package.json \
  --cover data/<日期>-<关键词>/publish/cover.png \
  --strict --write-lock

python3 scripts/xhs-publish.py \
  --input data/<日期>-<关键词>/post-package.json \
  --cover data/<日期>-<关键词>/publish/cover.png \
  --publish
```

发布器会选择新版创作页中的“上传图文”入口，并使用新版发布控件。它只接受已锁定且内容完全一致的版本。

## 核心脚本

| 文件 | 用途 |
| --- | --- |
| `scripts/xhs-search.py` | 检索小红书关键词与热门笔记数据 |
| `scripts/xhs-cover-research.py` | 每次封面前收集同主题高互动封面，下载为私有参考墙供视觉拆解 |
| `scripts/xhs-scene-prompt.py` | 将每篇照片型封面的专属视觉策划转成可用于生成无文字底图的提示 |
| `scripts/xhs-cover.py` | 生成一张 3:4、中文排版稳定的强小红书风格封面 |
| `scripts/xhs-carousel.py` | 生成多页轮播图 |
| `scripts/xhs-style-check.py` | 校验文案、封面风格与最终版本锁 |
| `scripts/xhs-publish.py` | 发布已锁定的图文笔记 |
| `references/post-package.md` | `post-package.json` 单一事实源的字段说明 |
| `references/style-qa.md` | 文案与封面的风格验收标准 |

## 依赖与登录

### 选题调研

调研能力依赖 [`xhs-cli`](https://github.com/jackwener/xhs-cli)：

```bash
pipx install xhs-cli
xhs login
```

首次登录需要在本机完成小红书授权。Cookie 由 `xhs-cli` 管理，Skill 不应提交或分享任何登录材料。

### 封面与图片

- Python 3.8+
- 可用的中文字体
- Pillow（用于把私有参考封面汇总为参考墙；未安装时仍会保留单张参考图）
- 可选：图像生成能力，用于创建没有文字的场景底图

没有图像生成能力时，`xhs-cover.py` 仍会生成可直接使用的信息型封面。

## 项目结构

```text
xhs-content/
├── SKILL.md
├── README.md
├── README.en.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── prompt.md
│   ├── post-package.md
│   ├── style-qa.md
│   └── carousel.md
└── scripts/
    ├── xhs-search.py
    ├── xhs-cover-research.py
    ├── xhs-scene-prompt.py
    ├── xhs-cover.py
    ├── xhs-carousel.py
    ├── xhs-style-check.py
    └── xhs-publish.py
```

## 注意事项

- 小红书网页结构和反爬策略可能变化；调研登录过期时，请重新执行 `xhs login`。
- 发布是对外动作，必须在用户确认最终版本后进行。
- 不要把二维码、Cookie、创作页登录信息、未确认草稿或测试产物提交到仓库。
- 不要提交或上传 `cover-research/` 中的第三方参考图。它们只用于本次封面的视觉分析。

## License

[MIT](./LICENSE)
