from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

from app.exceptions import BadRequestDataException, UserNotExistsException
from app.repositories import user as user_repository
from app.schemas import RequestUserLoginModel, TokenResponseModel

async def login(session: AsyncSession, credentials: RequestUserLoginModel) -> TokenResponseModel:
    user = await user_repository.get_user_by_email(session, credentials.email)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise BadRequestDataException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenResponseModel(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


async def refresh(session: AsyncSession, refresh_token: str) -> TokenResponseModel:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise BadRequestDataException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    if payload.get("type") != "refresh":
        raise BadRequestDataException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    user_id = int(payload["sub"])
    user = await user_repository.get_user_by_id(session, user_id)
    if not user:
        raise UserNotExistsException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return TokenResponseModel(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
