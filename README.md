# xhs-content

面向 Codex / OpenClaw 的小红书图文创作 Skill。它用同一个 `post-package.json` 管理标题、完整正文、话题、封面和发布内容，避免预览文案、最终图片和实际发布版本对不上。

[English](./README.en.md) | **中文**

## 能做什么

| 能力 | 产物 |
| --- | --- |
| 选题调研 | 小红书搜索结果、常见标题切口、评论问题和差异化角度 |
| 图文笔记 | 一篇完整的中文小红书正文、话题和一张 3:4 封面 |
| 封面调研 | 同主题高互动封面的私有参考墙，用于拆解而非复用 |
| 场景型封面 | 本篇专属的主体、构图、留白和无文字场景图提示 |
| 轮播图 | 适合清单、步骤和对比的 2–10 页图文 |
| 最终发布 | 锁定标题、完整正文、话题和封面后再上传图文笔记 |

## 工作方式

1. **先研究同题材内容。** 对需要封面的笔记，先检索当前主题的高互动内容并查看私有参考图，只提炼赛道规律，不使用参考封面作为成品。
2. **再做一篇完整笔记。** 正文、话题、封面标题和视觉方向全部写入 `post-package.json`。
3. **按内容决定封面。** 宠物、门店、产品、旅行和人物故事使用与主题相关的场景图；职场观点或比较类内容在调研支持时可以是文字主导的编辑式封面。新封面不从固定模板库挑选。
4. **确认后才发布。** 发布前会锁定标题、完整正文、话题和封面。任何一项变化都会使锁失效，必须重新确认。

## 重要边界

- 默认交付是**完整文案 + 一张封面**；只有明确要求文字时才不出封面。
- 封面必须与主题一致：幼猫内容要看见幼猫，探店内容要看见门店或食物，产品内容要看见产品。
- 照片型封面需要一张新的、无文字的场景底图。`xhs-scene-prompt.py` 负责导出本篇的图片提示，**不直接生成图片**；需要由可用的图片生成能力或授权图片来源提供底图。
- 第三方参考封面只用于本地分析，不能作为最终封面、不能上传，也不应提交到仓库。
- 招生、政策、医疗、薪资、就业等事实性内容需要核验可靠来源；发布是对外动作，必须先得到用户对最终版本的明确确认。

## 安装

### Codex

```bash
git clone https://github.com/ffffff9331/xhs-content.git ~/.codex/skills/xhs-content
```

刷新 Codex 后，直接在对话中提出需求即可。

### OpenClaw

支持 Git 安装的 OpenClaw 环境可使用：

```bash
openclaw skills install git:ffffff9331/xhs-content@main
```

## 用法

下面以“周末城市骑行”为一组连续示例。实际使用时只需替换主题。

### 1. 直接做一篇图文笔记

```text
用 xhs-content 做一篇小红书笔记：第一次周末城市骑行，路线、补给和穿搭怎么安排才不狼狈？
要完整文案和一张封面，文案与封面都要有鲜明的小红书风格。
```

默认产物：

```text
data/<日期>-<关键词>/
├── post-package.json
├── cover-research/
└── publish/
    ├── cover.svg
    └── cover.png
```

### 2. 先调研，再决定选题

```text
查找“周末城市骑行”相关的小红书热门内容，给我趋势报告；
再从中选一个有差异化的角度，做成完整文案和一张封面。
```

调研会额外生成 `sources.jsonl`、`report.md` 和私有的 `cover-research/`。封面研究目录内的图片不能发布或提交。

### 3. 做成轮播图

```text
把“第一次周末城市骑行：出发前 5 件事别漏掉”做成 6 页小红书轮播图。
```

轮播图适合步骤、清单和对比；首图仍按封面的调研与风格规则制作。

## 照片型封面

场景型封面先在 `post-package.json` 中写清具体主体、场景、镜头、文字留白和禁止元素。然后导出本篇独有的图片提示：

```bash
python3 scripts/xhs-scene-prompt.py \
  --input data/<日期>-<关键词>/post-package.json \
  --json
```

用这个提示生成或取得一张**无嵌入文字、无中文、无水印**的 3:4 场景图，保存为 `publish/background.png`，再合成封面：

```bash
python3 scripts/xhs-cover.py \
  --input data/<日期>-<关键词>/post-package.json \
  --background data/<日期>-<关键词>/publish/background.png \
  --out-dir data/<日期>-<关键词>/publish
```

如果调研结论支持纯文字的观点封面，可以在视觉蓝图中明确关闭背景图；不要为了“看起来统一”给每个题材强行套同一种照片或版式。

## 发布已确认版本

只有用户确认标题、完整正文、话题、封面、可见范围和发布时间后，才能运行：

```bash
python3 scripts/xhs-style-check.py \
  --input data/<日期>-<关键词>/post-package.json \
  --cover data/<日期>-<关键词>/publish/cover.png \
  --strict --require-visual --require-cover-research --write-lock

python3 scripts/xhs-publish.py \
  --input data/<日期>-<关键词>/post-package.json \
  --cover data/<日期>-<关键词>/publish/cover.png \
  --publish
```

发布器会使用当前创作服务平台的“上传图文”入口。只有锁与当前标题、正文、话题、封面完全一致时才会继续；登录、验证码、声明弹窗或非预期页面会停止并要求人工接手。

## 依赖

- Python 3.8+
- 可用的中文字体
- [`xhs-cli`](https://github.com/jackwener/xhs-cli)，用于搜索、登录和发布
- Pillow（可选，用于生成本地封面参考墙）
- 可选的图片生成能力，或可合法使用的无文字场景图

首次使用小红书搜索或发布前，需要在本机完成：

```bash
xhs login
```

Cookie、二维码、登录信息、未确认草稿、测试结果和 `cover-research/` 内第三方图片都不应提交到仓库。

## 核心文件

| 文件 | 作用 |
| --- | --- |
| `SKILL.md` | Skill 的执行规则 |
| `references/post-package.md` | `post-package.json` 字段说明 |
| `scripts/xhs-search.py` | 主题搜索 |
| `scripts/xhs-cover-research.py` | 同题材封面研究 |
| `scripts/xhs-scene-prompt.py` | 生成本篇场景图提示 |
| `scripts/xhs-cover.py` | 渲染中文封面 |
| `scripts/xhs-carousel.py` | 渲染轮播图 |
| `scripts/xhs-style-check.py` | 风格校验与最终版本锁定 |
| `scripts/xhs-publish.py` | 上传锁定后的图文笔记 |

## License

[MIT](./LICENSE)
