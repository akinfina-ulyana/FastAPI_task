import typing

import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import decode_token
from app.exceptions import BadRequestDataException
from app.models import User
from app.repositories import user as user_repository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: typing.Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise BadRequestDataException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise BadRequestDataException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise BadRequestDataException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    if payload.get("type") != "access":
        raise BadRequestDataException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    user_id = int(payload["sub"])
    user = await user_repository.get_user_by_id(session, user_id)
    if not user:
        raise BadRequestDataException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user