# jimeng-mcp

**即梦 AI 的 MCP 服务** — 让 Claude、Cursor 等 AI 助手直接调用即梦的图片/视频生成能力。

[English](#english) | 中文

---

## 这是什么

[MCP（Model Context Protocol）](https://modelcontextprotocol.io/) 是 Anthropic 推出的开放协议，允许 AI 模型通过标准化接口调用外部工具和服务。

**jimeng-mcp** 将字节跳动旗下[即梦 AI](https://jimeng.jianying.com/) 的官方 Volcengine API 封装为 MCP 服务。接入后，你可以在 Claude、Cursor 等支持 MCP 的客户端里，用自然语言直接驱动即梦生成图片和视频——无需打开浏览器，无需手动上传，生成结果自动保存到本地。

## 能做什么

### 图片能力

| 工具 | 能力 | 底层模型 |
|---|---|---|
| `generate_image` | 文生图，支持 4.0 / 4.6 / 3.x 多模型 | 即梦图片系列 |
| `image_to_image` | 图生图，智能参考原图风格/内容进行编辑 | jimeng_i2i 3.0 |
| `inpaint_image` | 局部重绘：涂抹修改或消除画面元素 | inpaint |
| `upscale_image` | 智能超清：低清图片放大到 4K / 8K | Seedream SR |

### 视频能力

| 工具 | 能力 | 底层模型 |
|---|---|---|
| `generate_video` | 文生视频，720P / 1080P / Pro 三档 | 即梦视频 3.0 |
| `image_to_video` | 图生视频：首帧、首尾帧、重新运镜、Pro 模式 | 即梦视频 3.0 |
| `imitate_motion` | 动作模仿：将参考视频的动作迁移到目标人物 | DreamActor 2.0 |
| `generate_digital_human` | 数字人：图片 + 音频 → 口型同步说话视频 | OmniHuman 1.5 |
| `translate_video` | 视频翻译：保留音色，口型同步换语言 | 翻译 2.0 |

## 使用场景

- **内容创作者**：对话式生成配图和视频素材，不切换工具
- **产品/设计**：在 Cursor 里边改需求文档边生成原型图
- **营销团队**：批量生成不同风格的创意图，描述即出图
- **开发者**：在自己的 AI 应用中集成即梦能力，无需关心鉴权细节

## 快速上手

### 第一步：开通服务

1. 登录[火山引擎控制台](https://console.volcengine.com/ai/ability/detail/2)，开通**即梦 AI** 服务
2. 在[访问控制 → API 访问密钥](https://console.volcengine.com/iam/keymanage/)获取 Access Key ID 和 Secret Access Key

### 第二步：安装

推荐使用 `uvx`（无需手动安装，运行时自动拉取）：

```bash
uvx jimeng-ai-mcp
```

也可以用 pip 全局安装：

```bash
pip install jimeng-ai-mcp
```

### 第三步：配置 MCP 客户端

#### Claude Desktop

配置文件路径：`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "jimeng": {
      "command": "uvx",
      "args": ["jimeng-ai-mcp"],
      "env": {
        "JIMENG_ACCESS_KEY_ID": "填入你的 Access Key ID",
        "JIMENG_SECRET_ACCESS_KEY": "填入你的 Secret Access Key"
      }
    }
  }
}
```

#### Cursor

配置文件路径：`~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "jimeng": {
      "command": "uvx",
      "args": ["jimeng-ai-mcp"],
      "env": {
        "JIMENG_ACCESS_KEY_ID": "填入你的 Access Key ID",
        "JIMENG_SECRET_ACCESS_KEY": "填入你的 Secret Access Key"
      }
    }
  }
}
```

> 重启客户端后，在对话框里直接输入指令即可，例如："帮我生成一张赛博朋克风格的城市夜景图"

### 本地开发模式

```bash
git clone https://github.com/andyleimc-source/jimeng-mcp

cd jimeng-mcp
cp .env.example .env
# 用编辑器打开 .env，填入两个密钥
uv sync
uv run jimeng-mcp
```

本地调试（启动 MCP Inspector）：

```bash
uv run mcp dev src/jimeng_mcp/server.py
```

## 使用示例

以下是在 Claude Desktop 中的实际对话示例：

**文生图**
> 帮我生成一张宋代山水画风格的图片，16:9 横幅，用即梦 4.0 模型

**图生图**
> 把这张产品图的背景换成简洁的白色摄影棚风格，保留产品主体不变
> [附上图片 URL]

**文生视频**
> 生成一段 10 秒的视频：一只狐狸在雪地里奔跑，慢镜头，电影感，16:9

**图生视频（首尾帧）**
> 我有两张图，帮我生成首尾帧驱动的视频，开头是这张日出照片，结尾是这张夕阳照片，5 秒
> 首帧：[URL1]，尾帧：[URL2]

**数字人**
> 用这张人物图片和这段音频，生成一个口型同步的数字人视频，输出 1080P
> 图片：[URL]，音频：[URL]

**视频翻译**
> 把这个中文视频翻译成英文，口型同步
> [视频 URL]

## 工具参数速查

### `generate_image`

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `prompt` | string | 必填 | 图片描述 |
| `model` | string | `jimeng_t2i_v40` | `jimeng_t2i_v40` / `jimeng_seedream46_cvtob` / `jimeng_t2i_v31` / `jimeng_t2i_v30` |
| `aspect_ratio` | string | `1:1` | `1:1` / `16:9` / `9:16` / `4:3` / `3:4` / `3:2` / `2:3` |
| `quality` | string | `2k` | `2k` 或 `normal` |
| `negative_prompt` | string | `""` | 不希望出现的内容 |

### `generate_video`

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `prompt` | string | 必填 | 视频描述 |
| `model` | string | `jimeng_t2v_v30` | `jimeng_t2v_v30`（720P）/ `jimeng_t2v_v30_1080p`（1080P）/ `jimeng_ti2v_v30_pro`（Pro） |
| `aspect_ratio` | string | `16:9` | `16:9` / `4:3` / `1:1` / `3:4` / `9:16` / `21:9` |
| `duration_sec` | int | `5` | `5` 或 `10` 秒 |

### `image_to_video`

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `image_url` | string | 必填 | 首帧图片 URL |
| `prompt` | string | 必填 | 视频描述 |
| `mode` | string | `first` | `first` / `first_1080p` / `first_tail` / `first_tail_1080p` / `recamera` / `pro` |
| `duration_sec` | int | `5` | `5` 或 `10` 秒 |
| `tail_image_url` | string | `""` | 尾帧图片（`first_tail` / `first_tail_1080p` 模式必填） |

### `translate_video`

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `video_url` | string | 必填 | 原视频 URL |
| `target_language` | string | 必填 | 目标语言代码 |
| `src_language` | string | `zh` | 源语言代码 |

语言代码：`zh` 中文 · `en` 英语 · `ja` 日语 · `ko` 韩语 · `fr` 法语 · `de` 德语 · `es` 西班牙语 · `pt` 葡萄牙语 · `ru` 俄语 · `ar` 阿拉伯语 · `it` 意大利语

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `JIMENG_ACCESS_KEY_ID` | ✅ | 火山引擎 Access Key ID |
| `JIMENG_SECRET_ACCESS_KEY` | ✅ | 火山引擎 Secret Access Key |
| `JIMENG_OUTPUT_DIR` | 可选 | 生成文件保存目录，默认 `~/jimeng-output` |

## 相关资源

- [即梦 AI 开放平台 — 接口总览](https://www.volcengine.com/docs/85621/1544716?lang=zh)
- [即梦 AI 官网](https://jimeng.jianying.com/)
- [火山引擎控制台](https://console.volcengine.com/ai/ability/detail/2)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [Claude Desktop 下载](https://claude.ai/download)
- [火山引擎签名机制文档](https://www.volcengine.com/docs/6369/65)

## License

[MIT](LICENSE)

---

## English

**jimeng-mcp** is an MCP (Model Context Protocol) server for [Jimeng AI](https://jimeng.jianying.com/) (即梦 · ByteDance). It wraps the official Volcengine API, letting Claude, Cursor, and other MCP-compatible AI clients generate images and videos through natural language — no browser switching, no manual uploads, results saved locally.

### What is MCP?

[Model Context Protocol](https://modelcontextprotocol.io/) is an open standard by Anthropic that lets AI models call external tools and services through a standardized interface.

### Tools

| Tool | Description |
|---|---|
| `generate_image` | Text-to-image (4.0 / 4.6 / 3.x models) |
| `image_to_image` | Image editing with text guidance |
| `inpaint_image` | Local inpainting / object removal |
| `upscale_image` | AI upscaling to 4K / 8K |
| `generate_video` | Text-to-video (720P / 1080P / Pro) |
| `image_to_video` | Image-to-video (first frame / first+last frame / camera movement / Pro) |
| `imitate_motion` | Motion imitation 2.0 |
| `generate_digital_human` | Talking head video — image + audio → lip-synced video (OmniHuman 1.5) |
| `translate_video` | Video translation with lip-sync (2.0) |

### Prerequisites

1. Enable Jimeng AI in the [Volcengine Console](https://console.volcengine.com/ai/ability/detail/2)
2. Get Access Key ID and Secret Access Key from [IAM Key Management](https://console.volcengine.com/iam/keymanage/)

### Installation

Recommended — run with `uvx` (no install needed):

```bash
uvx jimeng-ai-mcp
```

Or install with pip:

```bash
pip install jimeng-ai-mcp
```

### Setup (Claude Desktop)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jimeng": {
      "command": "uvx",
      "args": ["jimeng-ai-mcp"],
      "env": {
        "JIMENG_ACCESS_KEY_ID": "your_access_key_id",
        "JIMENG_SECRET_ACCESS_KEY": "your_secret_access_key"
      }
    }
  }
}
```

Restart Claude Desktop. Then just ask: *"Generate a cyberpunk cityscape, 16:9 widescreen."*

### Resources

- [Jimeng AI Open Platform (Official Docs)](https://www.volcengine.com/docs/85621/1544716?lang=zh)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/download)
