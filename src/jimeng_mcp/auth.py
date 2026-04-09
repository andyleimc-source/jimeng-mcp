"""
Volcengine HMAC-SHA256 签名实现
移植自 volcengine-ai/lib/auth.ts
"""

import hashlib
import hmac
import urllib.parse
from datetime import datetime, timezone


def _hmac_sha256(key: bytes, data: str) -> bytes:
    return hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()


def generate_signature(
    method: str,
    query: dict[str, str],
    headers: dict[str, str],
    body: str,
    access_key: str,
    secret_key: str,
    region: str,
    service: str,
    canonical_uri: str = "/",
) -> str:
    # 1. Canonical query string (sorted, percent-encoded)
    sorted_query = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
        for k, v in sorted(query.items())
    )

    # 2. Canonical headers (sorted by original key name, values trimmed, keys lowercased)
    sorted_headers_str = "".join(
        f"{k.lower()}:{v.strip()}\n"
        for k, v in sorted(headers.items())
    )

    # 3. Signed headers list
    signed_headers = ";".join(k.lower() for k in sorted(headers.keys()))

    # 4. Hashed payload
    hashed_payload = hashlib.sha256(body.encode("utf-8")).hexdigest()

    # 5. Canonical request
    canonical_request = "\n".join([
        method,
        canonical_uri,
        sorted_query,
        sorted_headers_str,
        signed_headers,
        hashed_payload,
    ])

    # 6. String to sign
    algorithm = "HMAC-SHA256"
    timestamp = headers.get("X-Date") or headers.get("x-date")
    if not timestamp:
        raise ValueError("Missing X-Date header")

    date_stamp = timestamp[:8]
    credential_scope = f"{date_stamp}/{region}/{service}/request"
    hashed_canonical = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    string_to_sign = "\n".join([algorithm, timestamp, credential_scope, hashed_canonical])

    # 7. Signing key chain
    k_date = _hmac_sha256(secret_key.encode("utf-8"), date_stamp)
    k_region = _hmac_sha256(k_date, region)
    k_service = _hmac_sha256(k_region, service)
    k_signing = _hmac_sha256(k_service, "request")

    # 8. Signature
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    return (
        f"{algorithm} Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )


def build_signed_request(
    query: dict[str, str],
    body: str,
    access_key: str,
    secret_key: str,
    region: str = "cn-north-1",
    service: str = "cv",
    base_url: str = "https://visual.volcengineapi.com",
) -> tuple[str, dict[str, str]]:
    """Build signed URL + headers for a Volcengine API request."""
    parsed = urllib.parse.urlparse(base_url)
    canonical_uri = parsed.path or "/"

    # Build URL with sorted query params
    sorted_params = sorted(query.items())
    qs = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
        for k, v in sorted_params
    )
    url = f"{base_url}?{qs}" if qs else base_url

    # Timestamp in Volcengine format: 20240101T120000Z
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "X-Date": timestamp,
        "Host": parsed.netloc,
    }

    authorization = generate_signature(
        "POST",
        query,
        headers,
        body,
        access_key,
        secret_key,
        region,
        service,
        canonical_uri,
    )

    headers["Authorization"] = authorization
    return url, headers
