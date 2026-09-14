from decimal import Decimal
from typing import cast

from pydantic import EmailStr
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User, UserBalance
from app.schemas.enums import UserRoleEnum, UserStatusEnum


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return cast(User | None, result.scalar_one_or_none())

    async def get_user_by_id(
            self, user_id: int, with_balances: bool = False
    ) -> User | None:
        query = select(User).where(User.id == user_id)
        if with_balances:
            query = query.options(selectinload(User.user_balance))
        result = await self.session.execute(query)
        return cast(User | None, result.scalar_one_or_none())

    async def create_user(self, email: str, password_hash: str) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            status=UserStatusEnum.ACTIVE,
            role=UserRoleEnum.USER,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def create_user_balances(self, user_id: int, currencies: list[str]) -> None:
        balances = [UserBalance(user_id=user_id, currency=currency, amount=0) for currency in currencies]
        self.session.add_all(balances)
        await self.session.flush()

    async def get_all(
            self,
            user_id: int | None = None,
            email: str | None = None,
            user_status: UserStatusEnum | None = None,
    ) -> list[User]:
        query = (
            select(User)
            .options(selectinload(User.user_balance))
            .order_by(User.created.desc())
        )
        if user_id is not None:
            query = query.where(User.id == user_id)
        if email is not None:
            query = query.where(User.email == email)
        if user_status is not None:
            query = query.where(User.status == user_status)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_status(self, user_id: int, new_status: UserStatusEnum) -> None:
        await self.session.execute(
            update(User)
            .values(status=new_status)
            .where(User.id == user_id)
        )


class UserBalanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_and_currency(self, user_id: int, currency: str) -> UserBalance | None:
        result = await self.session.execute(
            select(UserBalance).where(
                (UserBalance.user_id == user_id)
                & (UserBalance.currency == currency)
            )
        )
        return cast(UserBalance | None, result.scalar_one_or_none())

    async def get_for_update(
            self, user_id: int, currency: str
    ) -> UserBalance | None:
        query = select(UserBalance).where(
            (UserBalance.user_id == user_id)
            & (UserBalance.currency == currency)
        ).with_for_update()
        result = await self.session.execute(query)
        return cast(UserBalance | None, result.scalar_one_or_none())

    async def add_amount(self, balance_id: int, delta: Decimal) -> None:
        await self.session.execute(
            update(UserBalance)
            .values(amount=UserBalance.amount + delta)
            .where(UserBalance.id == balance_id)
        )
