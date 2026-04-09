"""
即梦 AI 模型标识符 (req_key) 常量
所有值均来自官方接口文档，已全量核对。
"""

# ── 图片生成 ────────────────────────────────────────────────────────────────
IMAGE_GEN_V40   = "jimeng_t2i_v40"                    # 图片生成 4.0
IMAGE_GEN_V46   = "jimeng_seedream46_cvtob"            # 图片生成 4.6 (Seedream)
IMAGE_GEN_V31   = "jimeng_t2i_v31"                    # 文生图 3.1
IMAGE_GEN_V30   = "jimeng_t2i_v30"                    # 文生图 3.0
IMAGE_GEN_V21L  = "jimeng_high_aes_general_v21_L"     # 通用高美感 v2.1 Large

# ── 图生图 ───────────────────────────────────────────────────────────────────
IMAGE_I2I_V30   = "jimeng_i2i_v30"                    # 图生图 3.0 智能参考

# ── 图片编辑 ─────────────────────────────────────────────────────────────────
IMAGE_INPAINT   = "jimeng_image2image_dream_inpaint"   # 交互编辑 / 局部重绘
IMAGE_UPSCALE   = "jimeng_i2i_seed3_tilesr_cvtob"     # 智能超清（4K/8K 超分辨率）

# ── 视频生成（文生视频）─────────────────────────────────────────────────────
VIDEO_T2V_V30       = "jimeng_t2v_v30"                # 文生视频 3.0 720P
VIDEO_T2V_V30_1080P = "jimeng_t2v_v30_1080p"          # 文生视频 3.0 1080P

# ── 视频生成（图生视频 + 文生视频 Pro）─────────────────────────────────────
VIDEO_TI2V_V30_PRO  = "jimeng_ti2v_v30_pro"           # 视频生成 3.0 Pro 1080P（文/图生视频）

# ── 图生视频 3.0（720P）────────────────────────────────────────────────────
VIDEO_I2V_FIRST_V30      = "jimeng_i2v_first_v30"          # 首帧 720P
VIDEO_I2V_FIRST_TAIL_V30 = "jimeng_i2v_first_tail_v30"     # 首尾帧 720P
VIDEO_I2V_RECAMERA_V30   = "jimeng_i2v_recamera_v30"       # 重新运镜 720P

# ── 图生视频 3.0（1080P）───────────────────────────────────────────────────
VIDEO_I2V_FIRST_V30_1080      = "jimeng_i2v_first_v30_1080"       # 首帧 1080P
VIDEO_I2V_FIRST_TAIL_V30_1080 = "jimeng_i2v_first_tail_v30_1080"  # 首尾帧 1080P

# ── 动作模仿 ─────────────────────────────────────────────────────────────────
VIDEO_MOTION_V1  = "jimeng_dream_actor_m1_gen_video_cv"    # 动作模仿 v1
VIDEO_MOTION_V20 = "jimeng_dreamactor_m20_gen_video"       # 动作模仿 2.0

# ── 数字人（OmniHuman 1.5，两步流程）────────────────────────────────────────
DIGITAL_HUMAN_CREATE_ROLE_V15 = "jimeng_realman_avatar_picture_create_role_omni_v15"  # 步骤1：创建角色
DIGITAL_HUMAN_GEN_VIDEO_V15   = "jimeng_realman_avatar_picture_omni_v15"              # 步骤2：生成视频

# ── 视频翻译 ─────────────────────────────────────────────────────────────────
VIDEO_TRANSLATION = "video_translate_v2_cvtob"             # 视频翻译 2.0

# ── 素材提取 ─────────────────────────────────────────────────────────────────
MATERIAL_EXTRACT = "jimeng_i2i_extract_tiled_images"       # 素材提取（商品提取）

# ── 图片尺寸预设 ─────────────────────────────────────────────────────────────
IMAGE_SIZES: dict[str, dict[str, tuple[int, int]]] = {
    "2k": {
        "1:1":  (2048, 2048),
        "16:9": (2560, 1440),
        "9:16": (1440, 2560),
        "4:3":  (2304, 1728),
        "3:4":  (1728, 2304),
        "3:2":  (2496, 1664),
        "2:3":  (1664, 2496),
    },
    "normal": {
        "1:1":  (1024, 1024),
        "16:9": (1536, 864),
        "9:16": (864, 1536),
        "4:3":  (1360, 1020),
        "3:4":  (1020, 1360),
        "3:2":  (1440, 960),
        "2:3":  (960, 1440),
    },
}
