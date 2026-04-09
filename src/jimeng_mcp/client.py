"""
Volcengine 即梦 API 异步客户端
移植自 volcengine-ai/lib/task.ts
"""

import asyncio
import os
from dataclasses import dataclass, field

import httpx

try:
    from .auth import build_signed_request
except ImportError:
    from auth import build_signed_request  # type: ignore

BASE_URL = os.getenv("VOLCENGINE_BASE_URL", "https://visual.volcengineapi.com")
REGION = os.getenv("VOLCENGINE_REGION", "cn-north-1")
SERVICE = "cv"


def _get_creds() -> tuple[str, str]:
    access_key = os.getenv("JIMENG_ACCESS_KEY_ID")
    secret_key = os.getenv("JIMENG_SECRET_ACCESS_KEY")
    if not access_key or not secret_key:
        raise RuntimeError(
            "缺少凭证：请设置环境变量 JIMENG_ACCESS_KEY_ID 和 JIMENG_SECRET_ACCESS_KEY"
        )
    return access_key, secret_key


@dataclass
class PollResult:
    image_urls: list[str] = field(default_factory=list)
    binary_data: bytes | None = None
    video_url: str | None = None


async def submit_task(req_key: str, params: dict) -> str:
    """提交异步任务，返回 task_id。"""
    import json

    access_key, secret_key = _get_creds()
    query = {"Action": "CVSync2AsyncSubmitTask", "Version": "2022-08-31"}
    body = json.dumps({"req_key": req_key, **params})
    url, headers = build_signed_request(query, body, access_key, secret_key, REGION, SERVICE, BASE_URL)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, content=body.encode())

    if resp.status_code != 200:
        raise RuntimeError(f"提交任务失败 ({resp.status_code}): {resp.text}")

    data = resp.json()
    if data.get("code") != 10000 or not data.get("data", {}).get("task_id"):
        raise RuntimeError(f"提交任务失败: {data.get('message') or data}")

    return data["data"]["task_id"]


async def poll_task(
    task_id: str,
    req_key: str,
    max_attempts: int = 120,
    interval_sec: float = 2.0,
) -> PollResult:
    """轮询任务结果直到完成，返回 PollResult。"""
    import base64
    import json

    access_key, secret_key = _get_creds()

    for attempt in range(max_attempts):
        query = {"Action": "CVSync2AsyncGetResult", "Version": "2022-08-31"}
        body = json.dumps({"req_key": req_key, "task_id": task_id})
        url, headers = build_signed_request(query, body, access_key, secret_key, REGION, SERVICE, BASE_URL)

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, content=body.encode())

        if resp.status_code != 200:
            raise RuntimeError(f"查询任务失败 ({resp.status_code}): {resp.text}")

        data = resp.json()
        if data.get("code") != 10000:
            raise RuntimeError(f"查询任务失败: {data.get('message') or data}")

        result_data = data.get("data") or {}
        status = result_data.get("status")
        b64_list: list[str] = result_data.get("binary_data_base64") or []
        image_urls: list[str] = result_data.get("image_urls") or []
        video_url: str | None = result_data.get("video_url")

        # 优先返回 base64 图片数据
        if b64_list:
            return PollResult(binary_data=base64.b64decode(b64_list[0]))

        if status == "done":
            if video_url:
                return PollResult(video_url=video_url)
            if image_urls:
                return PollResult(image_urls=image_urls)

        if status == "fail":
            raise RuntimeError(f"任务失败: {data.get('message') or '生成失败'}")

        await asyncio.sleep(interval_sec)

    raise RuntimeError(f"任务超时（已等待 {max_attempts * interval_sec:.0f} 秒）")


async def submit_task_cv(req_key: str, params: dict) -> str:
    """提交任务（CVSubmitTask，用于数字人等接口），返回 task_id。"""
    import json

    access_key, secret_key = _get_creds()
    query = {"Action": "CVSubmitTask", "Version": "2022-08-31"}
    body = json.dumps({"req_key": req_key, **params})
    url, headers = build_signed_request(query, body, access_key, secret_key, REGION, SERVICE, BASE_URL)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, content=body.encode())

    if resp.status_code != 200:
        raise RuntimeError(f"提交任务失败 ({resp.status_code}): {resp.text}")

    data = resp.json()
    if data.get("code") != 10000 or not data.get("data", {}).get("task_id"):
        raise RuntimeError(f"提交任务失败: {data.get('message') or data}")

    return data["data"]["task_id"]


async def poll_task_cv(
    task_id: str,
    req_key: str,
    max_attempts: int = 200,
    interval_sec: float = 4.0,
) -> PollResult:
    """轮询任务结果（CVGetResult，用于数字人等接口）。"""
    import json

    access_key, secret_key = _get_creds()

    for _ in range(max_attempts):
        query = {"Action": "CVGetResult", "Version": "2022-08-31"}
        body = json.dumps({"req_key": req_key, "task_id": task_id})
        url, headers = build_signed_request(query, body, access_key, secret_key, REGION, SERVICE, BASE_URL)

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, content=body.encode())

        if resp.status_code != 200:
            raise RuntimeError(f"查询任务失败 ({resp.status_code}): {resp.text}")

        data = resp.json()
        if data.get("code") != 10000:
            raise RuntimeError(f"查询任务失败: {data.get('message') or data}")

        result_data = data.get("data") or {}
        status = result_data.get("status")
        video_url: str | None = result_data.get("video_url")

        if status == "done":
            if video_url:
                return PollResult(video_url=video_url)
            return PollResult()

        if status == "fail":
            raise RuntimeError(f"任务失败: {data.get('message') or '生成失败'}")

        await asyncio.sleep(interval_sec)

    raise RuntimeError(f"任务超时（已等待 {max_attempts * interval_sec:.0f} 秒）")


async def download_bytes(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(url)
    if resp.status_code != 200:
        raise RuntimeError(f"下载失败 ({resp.status_code}): {url}")
    return resp.content
