from decimal import Decimal
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Transaction
from app.schemas import TransactionStatusEnum


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, currency: str, amount: Decimal,
                     status: TransactionStatusEnum = TransactionStatusEnum.PROCESSED, ) -> Transaction:
        transaction = Transaction(user_id=user_id, currency=currency, amount=amount, status=status)
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        query = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.session.execute(query)
        return cast(Transaction | None, result.scalar_one_or_none())

    async def get_by_id_for_update(self, transaction_id: int) -> Transaction | None:
        query = (
            select(Transaction)
            .where(Transaction.id == transaction_id)
            .with_for_update()
        )
        result = await self.session.execute(query)
        return cast(Transaction | None, result.scalar_one_or_none())

    async def get_user_transaction(self, user_id: int, transaction_id: int):
        query = (
            select(Transaction).where(
                (Transaction.id == transaction_id) & (Transaction.user_id == user_id))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_transactions(self, user_id: int | None = None) -> list[Transaction]:
        query = select(Transaction).order_by(Transaction.created.desc())
        if user_id is not None:
            query = query.where(Transaction.user_id == user_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_status(self, transaction_id: int, new_status: TransactionStatusEnum) -> None:
        transaction = await self.get_by_id(transaction_id)
        if transaction is not None:
            transaction.status = new_status
            await self.session.flush()
