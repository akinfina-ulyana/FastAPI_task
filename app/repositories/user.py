from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserBalance

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, email: str, password_hash: str) -> User:
    user = User(email=email,
                password_hash=password_hash,
                status="ACTIVE",
                role="USER")
    session.add(user)
    await session.flush()
    return user


async def create_user_balances(session: AsyncSession, user_id: int, currencies: list[str]) -> None:
    balances = [UserBalance(user_id=user_id, currency=currency, amount=0) for currency in currencies]
    session.add_all(balances)
    await session.flush()


