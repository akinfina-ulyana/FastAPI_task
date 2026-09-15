from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_service, get_user_service
from app.schemas import (
    RequestRefreshTokenModel,
    RequestUserLoginModel,
    RequestUserRegisterModel,
    ResponseUserModel,
    TokenResponseModel,
)
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=ResponseUserModel, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: RequestUserRegisterModel,
        user_service: UserService = Depends(get_user_service),
) -> ResponseUserModel:
    return await user_service.register_user(user_data)


@router.post("/login", response_model=TokenResponseModel)
async def login(
    credentials: RequestUserLoginModel,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponseModel:
    return await auth_service.login(credentials)


@router.post("/refresh", response_model=TokenResponseModel)
async def refresh(
    body: RequestRefreshTokenModel,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponseModel:
    return await auth_service.refresh(body.refresh_token)
