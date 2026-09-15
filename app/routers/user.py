import typing

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_current_admin, get_current_user, get_user_service
from app.models import User
from app.schemas import RequestUserUpdateModel, ResponseUserModel
from app.schemas.enums import UserStatusEnum
from app.services.user import UserService

router = APIRouter(tags=["users"])


@router.get("/me", response_model=ResponseUserModel, status_code=status.HTTP_200_OK)
async def get_me(
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
) -> ResponseUserModel:
    return await user_service.get_profile(current_user)


@router.get("/users", response_model=list[ResponseUserModel], status_code=status.HTTP_200_OK)
async def get_users(
        user_id: typing.Optional[int] = None,
        email: typing.Optional[str] = None,
        user_status: typing.Optional[UserStatusEnum] = Query(default=None),
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(get_current_admin),
) -> list[ResponseUserModel]:
    return await user_service.get_all(user_id=user_id, email=email, user_status=user_status)


@router.get("/users/{user_id}", response_model=ResponseUserModel, status_code=status.HTTP_200_OK)
async def get_user(
        user_id: int,
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(get_current_admin),
) -> ResponseUserModel:
    return await user_service.get_by_id(user_id)


@router.patch("/users/{user_id}", response_model=ResponseUserModel)
async def patch_user(
        user_id: int,
        user: RequestUserUpdateModel,
        user_service: UserService = Depends(get_user_service),
        _: User = Depends(get_current_admin),
) -> ResponseUserModel:
    return await user_service.update_status(user_id, user.status)
