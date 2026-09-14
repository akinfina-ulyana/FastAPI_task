from decimal import Decimal
from typing import cast

from app.core.uow import UnitOfWork
from app.exceptions import (
    BalanceNotFoundException,
    CreateTransactionForBlockedUserException,
    NegativeBalanceException,
    TransactionAlreadyRollbackedException,
    TransactionDoesNotBelongToUserException,
    TransactionNotExistsException,
    TransactionZeroAmountException,
    UpdateTransactionForBlockedUserException,
    UserNotExistsException,
)
from app.models import Transaction, User
from app.schemas import RequestTransactionModel
from app.schemas.enums import TransactionStatusEnum, UserStatusEnum


class TransactionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_transaction(
        self, user: User, data: RequestTransactionModel
    ) -> Transaction:
        if data.amount == 0:
            raise TransactionZeroAmountException()

        if user.status != UserStatusEnum.ACTIVE:
            raise CreateTransactionForBlockedUserException(
                detail=f"User with id=`{user.id}` is blocked"
            )

        balance = await self.uow.balances.get_for_update(user.id, data.currency.value)
        if not balance:
            raise BalanceNotFoundException(
                detail=f"Balance for currency {data.currency} not found"
            )

        new_amount = Decimal(balance.amount) + Decimal(data.amount)
        if new_amount < 0:
            raise NegativeBalanceException(detail="Negative balance")

        await self.uow.balances.add_amount(balance.id, Decimal(data.amount))
        transaction = await self.uow.transactions.create(
            user.id, data.currency.value, Decimal(data.amount)
        )
        await self.uow.commit()
        return transaction

    async def rollback_transaction(self, user: User, transaction_id: int) -> Transaction:
        transaction = await self.uow.transactions.get_by_id_for_update(transaction_id)
        if not transaction:
            raise TransactionNotExistsException(
                detail=f"Transaction with id=`{transaction_id}` does not exist"
            )
        if transaction.user_id != user.id:
            raise TransactionDoesNotBelongToUserException(
                detail=(
                    f"Transaction with id=`{transaction_id}` does not belong "
                    f"to user with id=`{user.id}`"
                )
            )
        if transaction.status == TransactionStatusEnum.ROLLBACKED:
            raise TransactionAlreadyRollbackedException(
                detail=f"Transaction with id=`{transaction_id}` is already rollbacked"
            )
        if user.status == UserStatusEnum.BLOCKED:
            raise UpdateTransactionForBlockedUserException(
                detail=f"User with id=`{user.id}` is blocked"
            )

        balance = await self.uow.balances.get_for_update(user.id, transaction.currency)
        if not balance:
            raise BalanceNotFoundException(
                detail=f"Balance for currency {transaction.currency} not found"
            )

        # Applying a transaction did `balance += amount`.
        # Rollback reverses it: `balance -= amount`.
        new_amount = Decimal(balance.amount) - Decimal(transaction.amount)
        if new_amount < 0:
            raise NegativeBalanceException(detail=f"Negative balance: {new_amount}")

        await self.uow.balances.add_amount(balance.id, -Decimal(transaction.amount))
        await self.uow.transactions.update_status(
            transaction_id, TransactionStatusEnum.ROLLBACKED
        )
        await self.uow.commit()
        transaction.status = TransactionStatusEnum.ROLLBACKED
        return transaction

    async def get_user_transactions(self, user_id: int) -> list[Transaction]:
        return await self.uow.transactions.get_user_transactions(user_id)

    async def get_all_transactions(self) -> list[Transaction]:
        return await self.uow.transactions.get_user_transactions(user_id=None)

    async def get_user_transaction(self, user: User, transaction_id: int) -> Transaction:
        transaction = await self.uow.transactions.get_user_transaction(user.id, transaction_id)
        if not transaction:
            raise TransactionNotExistsException(
                detail=f"Transaction with id=`{transaction_id}` does not exist"
            )
        return cast(Transaction, transaction)

    async def _ensure_user_exists(self, user_id: int) -> User:
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotExistsException(
                detail=f"User with id=`{user_id}` does not exist"
            )
        return user
