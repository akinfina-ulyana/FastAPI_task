from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models import User
from app.dependencies import get_current_user
from app.schemas import (
    RequestRefreshTokenModel,
    RequestUserLoginModel,
    RequestUserRegisterModel,
    TokenResponseModel,
    UserModel,
)
from app.services import auth as auth_service, user as user_service

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RequestUserRegisterModel,
    session: AsyncSession = Depends(get_async_session),
) -> UserModel:
    return await user_service.register_user(session, user_data)


@router.post("/login", response_model=TokenResponseModel)
async def login(
    credentials: RequestUserLoginModel,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponseModel:
    return await auth_service.login(session, credentials)


@router.post("/refresh", response_model=TokenResponseModel)
async def refresh(
    body: RequestRefreshTokenModel,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponseModel:
    return await auth_service.refresh(session, body.refresh_token)


@router.get("/me", response_model=UserModel)
async def me(current_user: User = Depends(get_current_user)) -> UserModel:
    return UserModel(
        id=current_user.id,
        email=current_user.email,
        status=current_user.status,
        created=current_user.created,
    )