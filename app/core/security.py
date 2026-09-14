import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return str(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bool(bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8")))
    except (ValueError, TypeError):
        return False


def create_token(subject: str | int, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
        "jti": secrets.token_hex(16),
    }
    encode = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return cast(str, encode)


def create_access_token(user_id: int | str) -> str:
    return create_token(
        user_id,
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int | str) -> str:
    return create_token(
        user_id,
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return cast(dict[str, Any], decoded)
