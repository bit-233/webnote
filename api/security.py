import hashlib
import secrets
import time
from collections import defaultdict, deque
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from config import APP_CONFIG

FAILED_LOGIN_ATTEMPTS = defaultdict(deque)
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300


def _expected_token() -> Optional[str]:
    password = APP_CONFIG.get("ADMIN_PASSWORD", "")
    if not password:
        return None
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _prune_attempts(client_key: str) -> deque:
    window_start = time.time() - WINDOW_SECONDS
    attempts = FAILED_LOGIN_ATTEMPTS[client_key]
    while attempts and attempts[0] < window_start:
        attempts.popleft()
    return attempts


def require_auth(session_token: Optional[str] = Cookie(default=None, alias=APP_CONFIG["COOKIE_NAME"])):
    expected = _expected_token()
    if not expected:
        return True
    if not secrets.compare_digest(str(session_token or ""), expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="需要登录")
    return True


def login(password: str, request: Request):
    expected = _expected_token()
    if expected is None:
        return JSONResponse({"message": "无需登录"})
    client_key = request.client.host if request.client else "unknown"
    attempts = _prune_attempts(client_key)
    if len(attempts) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="尝试次数过多，请稍后再试",
        )

    submitted_token = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if not secrets.compare_digest(submitted_token, expected):
        attempts.append(time.time())
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")

    FAILED_LOGIN_ATTEMPTS.pop(client_key, None)
    response = JSONResponse({"message": "登录成功"})
    response.set_cookie(
        APP_CONFIG["COOKIE_NAME"],
        expected,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response


def logout():
    response = JSONResponse({"message": "已登出"})
    response.delete_cookie(APP_CONFIG["COOKIE_NAME"])
    return response
