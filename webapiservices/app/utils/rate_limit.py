import time
from fastapi import Request

from app.utils.exceptions import RateLimitException, ErrorCode

_rate_limit_store: dict[str, list[float]] = {}


def _get_limit_key(request: Request) -> str:
    from app.utils.security import decode_token
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        user_id = decode_token(token)
        if user_id:
            return f"user:{user_id}"
    api_key = request.query_params.get("api_key")
    if api_key:
        return f"apikey:{api_key[:16]}"
    client = request.client
    return f"ip:{client.host if client else 'unknown'}"


def check_rate_limit(request: Request, max_requests: int = 60, window_seconds: int = 60):
    key = _get_limit_key(request)
    now = time.time()

    timestamps = _rate_limit_store.get(key, [])
    timestamps = [t for t in timestamps if now - t < window_seconds]

    if len(timestamps) >= max_requests:
        raise RateLimitException(
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED[0],
            error_desc=ErrorCode.RATE_LIMIT_EXCEEDED[1],
            status_code=429,
            debug_info=f"Limit: {max_requests} requests per {window_seconds} seconds. Key: {key}",
        )

    timestamps.append(now)
    _rate_limit_store[key] = timestamps


def rate_limit_dependency(max_requests: int = 60, window_seconds: int = 60):
    def _check(request: Request):
        check_rate_limit(request, max_requests, window_seconds)
    return _check
