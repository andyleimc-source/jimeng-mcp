"""
即梦 AI MCP Server
覆盖即梦全部官方 API 能力（基于 Volcengine 官方接口文档）
"""

import base64
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

try:
    from .client import download_bytes, poll_task, poll_task_cv, submit_task, submit_task_cv
    from .models import (
        DIGITAL_HUMAN_GEN_VIDEO_V15,
        IMAGE_GEN_V21L,
        IMAGE_GEN_V30,
        IMAGE_GEN_V31,
        IMAGE_GEN_V40,
        IMAGE_GEN_V46,
        IMAGE_I2I_V30,
        IMAGE_INPAINT,
        IMAGE_SIZES,
        IMAGE_UPSCALE,
        VIDEO_I2V_FIRST_TAIL_V30,
        VIDEO_I2V_FIRST_TAIL_V30_1080,
        VIDEO_I2V_FIRST_V30,
        VIDEO_I2V_FIRST_V30_1080,
        VIDEO_I2V_RECAMERA_V30,
        VIDEO_MOTION_V20,
        VIDEO_T2V_V30,
        VIDEO_T2V_V30_1080P,
        VIDEO_TI2V_V30_PRO,
        VIDEO_TRANSLATION,
    )
except ImportError:
    from client import download_bytes, poll_task, poll_task_cv, submit_task, submit_task_cv  # type: ignore
    from models import (  # type: ignore
        DIGITAL_HUMAN_GEN_VIDEO_V15,
        IMAGE_GEN_V21L,
        IMAGE_GEN_V30,
        IMAGE_GEN_V31,
        IMAGE_GEN_V40,
        IMAGE_GEN_V46,
        IMAGE_I2I_V30,
        IMAGE_INPAINT,
        IMAGE_SIZES,
        IMAGE_UPSCALE,
        VIDEO_I2V_FIRST_TAIL_V30,
        VIDEO_I2V_FIRST_TAIL_V30_1080,
        VIDEO_I2V_FIRST_V30,
        VIDEO_I2V_FIRST_V30_1080,
        VIDEO_I2V_RECAMERA_V30,
        VIDEO_MOTION_V20,
        VIDEO_T2V_V30,
        VIDEO_T2V_V30_1080P,
        VIDEO_TI2V_V30_PRO,
        VIDEO_TRANSLATION,
    )

load_dotenv()

mcp = FastMCP("jimeng")


# ── 输出目录 ─────────────────────────────────────────────────────────────────
def _output_dir() -> Path:
    d = Path(os.getenv("JIMENG_OUTPUT_DIR", "~/jimeng-output")).expanduser()
    d.mkdir(parents=True, exist_ok=True)
    return d


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _save_image(data: bytes, suffix: str = "image") -> Path:
    path = _output_dir() / f"{_timestamp()}-{suffix}.jpg"
    path.write_bytes(data)
    return path


def _save_video(data: bytes, suffix: str = "video") -> Path:
    path = _output_dir() / f"{_timestamp()}-{suffix}.mp4"
    path.write_bytes(data)
    return path


def _image_size(aspect_ratio: str, quality: str) -> tuple[int, int]:
    sizes = IMAGE_SIZES.get(quality, IMAGE_SIZES["2k"])
    return sizes.get(aspect_ratio, sizes["1:1"])


# ════════════════════════════════════════════════════════════════════════════
# 图片生成
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def generate_image(
    prompt: str,
    model: str = "jimeng_t2i_v40",
    aspect_ratio: str = "1:1",
    quality: str = "2k",
    negative_prompt: str = "",
) -> str:
    """
    文生图：根据文字描述生成图片。

    - model（模型版本）：
        - jimeng_t2i_v40               图片生成 4.0（默认，推荐）
        - jimeng_seedream46_cvtob      图片生成 4.6（Seedream，支持最高 4K）
        - jimeng_t2i_v31               文生图 3.1
        - jimeng_t2i_v30               文生图 3.0
        - jimeng_high_aes_general_v21_L  通用高美感 v2.1
    - aspect_ratio: 1:1 / 16:9 / 9:16 / 4:3 / 3:4 / 3:2 / 2:3
    - quality: 2k（默认）/ normal
    - negative_prompt: 负面提示词（可选，部分模型不支持）
    """
    width, height = _image_size(aspect_ratio, quality)
    params: dict = {"prompt": prompt, "width": width, "height": height}
    if negative_prompt:
        params["negative_prompt"] = negative_prompt

    task_id = await submit_task(model, params)
    result = await poll_task(task_id, model, max_attempts=60, interval_sec=2)

    if result.binary_data:
        path = _save_image(result.binary_data, "generate")
        b64 = base64.b64encode(result.binary_data).decode()
        return (
            f"✅ 图片生成完成\n"
            f"📁 已保存：{path}\n"
            f"🖼️ 预览（base64）：data:image/jpeg;base64,{b64[:80]}..."
        )

    if result.image_urls:
        urls_md = "\n".join(f"- {u}" for u in result.image_urls)
        return f"✅ 图片生成完成\n\n{urls_md}"

    return "❌ 未收到图片数据"


@mcp.tool()
async def image_to_image(
    prompt: str,
    image_url: str,
    aspect_ratio: str = "1:1",
    quality: str = "2k",
    scale: float = 0.5,
) -> str:
    """
    图生图（智能参考）：参考输入图片，结合文字描述编辑或生成新图片。
    使用即梦图生图 3.0 模型（jimeng_i2i_v30）。

    - image_url: 参考图片 URL（JPEG/PNG，最大 4.7MB，最大 4096×4096）
    - aspect_ratio: 1:1 / 16:9 / 9:16 / 4:3 / 3:4 / 3:2 / 2:3
    - quality: 2k（默认）/ normal
    - scale: 文本影响程度 0.0～1.0（默认 0.5，越大越贴近文字描述，越小越保留原图）
    """
    width, height = _image_size(aspect_ratio, quality)
    params = {
        "prompt": prompt,
        "image_urls": [image_url],
        "width": width,
        "height": height,
        "scale": scale,
    }

    task_id = await submit_task(IMAGE_I2I_V30, params)
    result = await poll_task(task_id, IMAGE_I2I_V30, max_attempts=60, interval_sec=2)

    if result.binary_data:
        path = _save_image(result.binary_data, "i2i")
        return f"✅ 图生图完成\n📁 已保存：{path}"

    if result.image_urls:
        urls_md = "\n".join(f"- {u}" for u in result.image_urls)
        return f"✅ 图生图完成\n\n{urls_md}"

    return "❌ 未收到图片数据"


@mcp.tool()
async def inpaint_image(
    prompt: str,
    image_url: str,
    mask_url: str,
) -> str:
    """
    局部重绘（Inpainting）：在图片的指定区域（mask）内根据提示词重新生成内容。
    使用即梦交互编辑模型（jimeng_image2image_dream_inpaint）。

    - image_url: 原图 URL（JPEG/PNG，最大 4.7MB）
    - mask_url: 遮罩图 URL（单通道灰度图，白色=重绘区域，黑色=保留区域）
    - prompt: 重绘内容描述；输入"删除"可消除选区内容
    """
    params = {
        "prompt": prompt,
        "image_urls": [image_url, mask_url],
    }

    task_id = await submit_task(IMAGE_INPAINT, params)
    result = await poll_task(task_id, IMAGE_INPAINT, max_attempts=60, interval_sec=2)

    if result.binary_data:
        path = _save_image(result.binary_data, "inpaint")
        return f"✅ 局部重绘完成\n📁 已保存：{path}"

    if result.image_urls:
        urls_md = "\n".join(f"- {u}" for u in result.image_urls)
        return f"✅ 局部重绘完成\n\n{urls_md}"

    return "❌ 未收到图片数据"


@mcp.tool()
async def upscale_image(
    image_url: str,
    resolution: str = "4k",
    detail: int = 50,
) -> str:
    """
    智能超清：将图片放大并增强细节至 4K 或 8K 分辨率。
    使用即梦智能超清模型（jimeng_i2i_seed3_tilesr_cvtob）。

    - image_url: 输入图片 URL（JPEG/PNG，最大 4.7MB，最大 4096×4096）
    - resolution: "4k"（默认）或 "8k"
    - detail: 细节生成程度 0～100（默认 50，越大细节越多但可能偏离原图）
    """
    params = {
        "image_urls": [image_url],
        "resolution": resolution,
        "scale": detail,
    }

    task_id = await submit_task(IMAGE_UPSCALE, params)
    result = await poll_task(task_id, IMAGE_UPSCALE, max_attempts=60, interval_sec=3)

    if result.binary_data:
        path = _save_image(result.binary_data, "upscale")
        return f"✅ 智能超清完成\n📁 已保存：{path}"

    if result.image_urls:
        urls_md = "\n".join(f"- {u}" for u in result.image_urls)
        return f"✅ 智能超清完成\n\n{urls_md}"

    return "❌ 未收到图片数据"


# ════════════════════════════════════════════════════════════════════════════
# 视频生成（文生视频）
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def generate_video(
    prompt: str,
    model: str = "jimeng_t2v_v30",
    aspect_ratio: str = "16:9",
    duration_sec: int = 5,
) -> str:
    """
    文生视频：根据文字描述生成视频（约需 1～5 分钟）。

    - model（模型版本）：
        - jimeng_t2v_v30        视频生成 3.0 720P（默认）
        - jimeng_t2v_v30_1080p  视频生成 3.0 1080P
        - jimeng_ti2v_v30_pro   视频生成 3.0 Pro 1080P（效果更好）
    - aspect_ratio: 16:9 / 4:3 / 1:1 / 3:4 / 9:16 / 21:9
    - duration_sec: 5（默认）或 10
    """
    frames = 121 if duration_sec <= 5 else 241
    params = {
        "prompt": prompt,
        "seed": -1,
        "frames": frames,
        "aspect_ratio": aspect_ratio,
    }

    task_id = await submit_task(model, params)
    result = await poll_task(task_id, model, max_attempts=150, interval_sec=4)

    if result.video_url:
        data = await download_bytes(result.video_url)
        path = _save_video(data, "t2v")
        return (
            f"✅ 视频生成完成\n"
            f"📁 已保存：{path}\n"
            f"🔗 原始 URL：{result.video_url}"
        )

    return "❌ 未收到视频数据"


# ════════════════════════════════════════════════════════════════════════════
# 视频生成（图生视频）
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def image_to_video(
    image_url: str,
    prompt: str,
    mode: str = "first",
    duration_sec: int = 5,
    tail_image_url: str = "",
) -> str:
    """
    图生视频：将静态图片转换为动态视频（约需 1～5 分钟）。

    - image_url: 首帧图片 URL（JPEG/PNG，最大 4.7MB）
    - prompt: 视频内容描述（必填）
    - mode（模式）：
        - first           首帧驱动 720P（默认）
        - first_1080p     首帧驱动 1080P
        - first_tail      首尾帧驱动 720P（需提供 tail_image_url）
        - first_tail_1080p  首尾帧驱动 1080P（需提供 tail_image_url）
        - recamera        重新运镜 720P（需提供 template_id，通过 prompt 描述运镜效果）
        - pro             视频生成 3.0 Pro 1080P（首帧，效果更好）
    - duration_sec: 5（默认）或 10
    - tail_image_url: 尾帧图片 URL（仅 first_tail / first_tail_1080p 模式需要）

    recamera 模式可用运镜模板（在 prompt 中指定 template_id）：
    hitchcock_dolly_in / hitchcock_dolly_out / robo_arm / dynamic_orbit /
    central_orbit / crane_push / quick_pull_back / counterclockwise_swivel /
    clockwise_swivel / handheld / rapid_push_pull
    """
    frames = 121 if duration_sec <= 5 else 241

    mode_map = {
        "first":            VIDEO_I2V_FIRST_V30,
        "first_1080p":      VIDEO_I2V_FIRST_V30_1080,
        "first_tail":       VIDEO_I2V_FIRST_TAIL_V30,
        "first_tail_1080p": VIDEO_I2V_FIRST_TAIL_V30_1080,
        "recamera":         VIDEO_I2V_RECAMERA_V30,
        "pro":              VIDEO_TI2V_V30_PRO,
    }
    req_key = mode_map.get(mode, VIDEO_I2V_FIRST_V30)

    if mode in ("first_tail", "first_tail_1080p"):
        if not tail_image_url:
            return "❌ first_tail 模式需要提供 tail_image_url（尾帧图片 URL）"
        params: dict = {
            "image_urls": [image_url, tail_image_url],
            "prompt": prompt,
            "seed": -1,
            "frames": frames,
        }
    elif mode == "recamera":
        # prompt 里包含 template_id 和 camera_strength 说明，此处只传 prompt
        # 用户需在 prompt 里描述运镜效果；如需精确控制可传 template_id
        params = {
            "image_urls": [image_url],
            "prompt": prompt,
            "template_id": "dynamic_orbit",  # 默认动感环绕
            "camera_strength": "medium",
            "seed": -1,
            "frames": frames,
        }
    else:
        params = {
            "image_urls": [image_url],
            "prompt": prompt,
            "seed": -1,
            "frames": frames,
        }

    task_id = await submit_task(req_key, params)
    result = await poll_task(task_id, req_key, max_attempts=150, interval_sec=4)

    if result.video_url:
        data = await download_bytes(result.video_url)
        path = _save_video(data, "i2v")
        return (
            f"✅ 图生视频完成\n"
            f"📁 已保存：{path}\n"
            f"🔗 原始 URL：{result.video_url}"
        )

    return "❌ 未收到视频数据"


# ════════════════════════════════════════════════════════════════════════════
# 动作模仿
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def imitate_motion(
    image_url: str,
    video_url: str,
) -> str:
    """
    动作模仿 2.0：提取参考视频中的动作/表情/口型，迁移到目标人物图片上。
    使用模型：jimeng_dreamactor_m20_gen_video

    - image_url: 目标人物图片 URL（JPEG/PNG，480×480 以上，1920×1080 以内）
    - video_url: 动作参考视频 URL（MP4/MOV/WEBM，最长 30 秒）

    输出视频约需 3～5 分钟（10 秒视频约需 180 秒）。
    """
    params = {
        "image_urls": [image_url],
        "video_url": video_url,
    }

    task_id = await submit_task(VIDEO_MOTION_V20, params)
    result = await poll_task(task_id, VIDEO_MOTION_V20, max_attempts=200, interval_sec=5)

    if result.video_url:
        data = await download_bytes(result.video_url)
        path = _save_video(data, "motion")
        return (
            f"✅ 动作模仿完成\n"
            f"📁 已保存：{path}\n"
            f"🔗 原始 URL：{result.video_url}"
        )

    return "❌ 未收到视频数据"


# ════════════════════════════════════════════════════════════════════════════
# 数字人（OmniHuman 1.5）
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def generate_digital_human(
    portrait_url: str,
    audio_url: str,
    resolution: int = 1080,
    prompt: str = "",
) -> str:
    """
    数字人生成（OmniHuman 1.5）：驱动人物图片口型和动作，配合音频生成说话视频。
    使用模型：jimeng_realman_avatar_picture_omni_v15

    - portrait_url: 人物肖像图片 URL（含人物/动漫/宠物）
    - audio_url: 驱动音频 URL（WAV/MP3，必须小于 60 秒）
    - resolution: 输出分辨率，720 或 1080（默认 1080）
    - prompt: 可选提示词，支持中/英/日/韩语，最长 300 字符

    注意：此接口使用 CVSubmitTask/CVGetResult（与普通接口不同）。
    """
    params: dict = {
        "image_url": portrait_url,
        "audio_url": audio_url,
        "output_resolution": resolution,
        "pe_fast_mode": resolution == 720,
    }
    if prompt:
        params["prompt"] = prompt

    task_id = await submit_task_cv(DIGITAL_HUMAN_GEN_VIDEO_V15, params)
    result = await poll_task_cv(task_id, DIGITAL_HUMAN_GEN_VIDEO_V15, max_attempts=200, interval_sec=5)

    if result.video_url:
        data = await download_bytes(result.video_url)
        path = _save_video(data, "digital-human")
        return (
            f"✅ 数字人生成完成\n"
            f"📁 已保存：{path}\n"
            f"🔗 原始 URL：{result.video_url}"
        )

    return "❌ 未收到视频数据"


# ════════════════════════════════════════════════════════════════════════════
# 视频翻译
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def translate_video(
    video_url: str,
    target_language: str,
    src_language: str = "zh",
) -> str:
    """
    视频翻译 2.0：将视频中的语音翻译并口型同步为目标语言。
    使用模型：video_translate_v2_cvtob

    - video_url: 原始视频 URL（需公网可访问）
    - target_language: 目标语言缩写
    - src_language: 源语言缩写（默认 "zh" 中文）

    支持的语言代码：
    zh（中文）en（英语）ja（日语）ko（韩语）fr（法语）de（德语）
    es（西班牙语）pt（葡萄牙语）ru（俄语）ar（阿拉伯语）it（意大利语）
    hi（印地语）id（印尼语）nl（荷兰语）tr（土耳其语）pl（波兰语）等
    """
    params = {
        "video_url": video_url,
        "src_language": src_language,
        "target_language": target_language,
    }

    task_id = await submit_task(VIDEO_TRANSLATION, params)
    result = await poll_task(task_id, VIDEO_TRANSLATION, max_attempts=200, interval_sec=5)

    if result.video_url:
        data = await download_bytes(result.video_url)
        path = _save_video(data, "translated")
        return (
            f"✅ 视频翻译完成\n"
            f"📁 已保存：{path}\n"
            f"🔗 原始 URL：{result.video_url}"
        )

    return "❌ 未收到视频数据"


# ── 入口 ─────────────────────────────────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
