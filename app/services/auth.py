import jwt

from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.core.uow import UnitOfWork
from app.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserIsBlockedException,
    UserNotExistsException,
)
from app.schemas import RequestUserLoginModel, TokenResponseModel, UserStatusEnum


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def login(self, credentials: RequestUserLoginModel) -> TokenResponseModel:
        user = await self.uow.users.get_user_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.password_hash):
            raise InvalidCredentialsException()
        if user.status == UserStatusEnum.BLOCKED:
            raise UserIsBlockedException()
        return TokenResponseModel(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh(self, refresh_token: str) -> TokenResponseModel:
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError:
            raise InvalidTokenException("Invalid refresh token")
        if payload.get("type") != "refresh":
            raise InvalidTokenException("Invalid token type")
        try:
            user_id = int(payload["sub"])
        except (TypeError, ValueError, KeyError):
            raise InvalidTokenException("Invalid token payload")
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotExistsException()
        if user.status == UserStatusEnum.BLOCKED:
            raise UserIsBlockedException()
        return TokenResponseModel(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
