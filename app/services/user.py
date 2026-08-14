from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.exceptions import BadRequestDataException, UserAlreadyExistsException
from app.repositories import user as user_repository
from app.schemas import CurrencyEnum, RequestUserRegisterModel, UserModel


async def register_user(session: AsyncSession, user_data: RequestUserRegisterModel) -> UserModel:

    email = user_data.email.strip()
    if not email:
        raise BadRequestDataException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email can't be empty",
        )

    existing_user = await user_repository.get_user_by_email(session, email)
    if existing_user:
        raise UserAlreadyExistsException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email=`{email}` already exists",
        )

    password_hash = hash_password(user_data.password)
    user = await user_repository.create_user(session, email, password_hash)
    currencies = [currency.value for currency in CurrencyEnum]
    await user_repository.create_user_balances(session, user.id, currencies)
    await session.commit()

    return UserModel(id=user.id, email=user.email, status=user.status, created=user.created)
