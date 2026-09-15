import typing

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import decode_token
from app.core.uow import UnitOfWork
from app.exceptions import (
    AdminRoleRequiredException,
    InvalidTokenException,
    NotAuthenticatedException,
    TokenExpiredException,
    UserIsBlockedException,
)
from app.models import User
from app.schemas import UserStatusEnum
from app.services.auth import AuthService
from app.services.transaction import TransactionService
from app.services.user import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_uow(session: AsyncSession = Depends(get_async_session)) -> UnitOfWork:
    return UnitOfWork(session)


def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)


def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    return UserService(uow)


def get_transaction_service(uow: UnitOfWork = Depends(get_uow)) -> TransactionService:
    return TransactionService(uow)


async def get_current_user(
        credentials: typing.Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
        uow: UnitOfWork = Depends(get_uow)) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise NotAuthenticatedException()
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()
    if payload.get("type") != "access":
        raise InvalidTokenException("Invalid token type")
    sub = payload.get("sub")
    if sub is None:
        raise InvalidTokenException("Invalid token payload")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise InvalidTokenException("Invalid token payload")
    user = await uow.users.get_user_by_id(user_id)
    if not user:
        raise NotAuthenticatedException("User not found")
    if user.status == UserStatusEnum.BLOCKED:
        raise UserIsBlockedException()
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.value != "ADMIN":
        raise AdminRoleRequiredException()
    return current_user
