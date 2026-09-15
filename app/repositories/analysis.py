from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Transaction, User
from app.schemas.enums import CurrencyEnum, TransactionStatusEnum

EXCHANGE_RATES_TO_USD: dict[CurrencyEnum, float] = {
    CurrencyEnum.USD: 1.0,
    CurrencyEnum.EUR: 0.9342,
    CurrencyEnum.AUD: 0.5447,
    CurrencyEnum.CAD: 0.6162,
    CurrencyEnum.ARS: 0.0009,
    CurrencyEnum.PLN: 0.2343,
    CurrencyEnum.BTC: 100000.0,
    CurrencyEnum.ETH: 3557.3476,
    CurrencyEnum.DOGE: 0.3627,
    CurrencyEnum.USDT: 0.9709,
}


def to_usd(amount: Decimal, currency: str) -> Decimal:
    rate = EXCHANGE_RATES_TO_USD.get(CurrencyEnum(currency))
    if rate is None:
        raise KeyError(f"Unknown currency: {currency}")
    return Decimal(amount) * Decimal(str(rate))


class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_registered_users_count(self, dt_gt: date, dt_lt: date) -> int:
        result = await self.session.execute(
            select(func.count(User.id)).where(
                func.date(User.created) >= dt_gt,
                func.date(User.created) <= dt_lt,
            )
        )
        return int(result.scalar() or 0)

    async def get_registered_and_deposit_users_count(
        self, dt_gt: date, dt_lt: date
    ) -> int:
        registered = select(User.id).where(
            func.date(User.created) >= dt_gt,
            func.date(User.created) <= dt_lt,
        ).subquery()
        result = await self.session.execute(
            select(func.count()).select_from(registered).where(
                registered.c.id.in_(
                    select(Transaction.user_id).where(
                        func.date(Transaction.created) >= dt_gt,
                        func.date(Transaction.created) <= dt_lt,
                        Transaction.amount > 0,
                    )
                )
            )
        )
        return int(result.scalar() or 0)

    async def get_registered_and_not_rollbacked_deposit_users_count(
        self, dt_gt: date, dt_lt: date
    ) -> int:
        registered = select(User.id).where(
            func.date(User.created) >= dt_gt,
            func.date(User.created) <= dt_lt,
        ).subquery()
        result = await self.session.execute(
            select(func.count()).select_from(registered).where(
                registered.c.id.in_(
                    select(Transaction.user_id).where(
                        func.date(Transaction.created) >= dt_gt,
                        func.date(Transaction.created) <= dt_lt,
                        Transaction.amount > 0,
                        Transaction.status != TransactionStatusEnum.ROLLBACKED,
                    )
                )
            )
        )
        return int(result.scalar() or 0)

    async def get_not_rollbacked_deposit_amount(
        self, dt_gt: date, dt_lt: date
    ) -> Decimal:
        result = await self.session.execute(
            select(Transaction).where(
                func.date(Transaction.created) >= dt_gt,
                func.date(Transaction.created) <= dt_lt,
                Transaction.amount > 0,
                Transaction.status != TransactionStatusEnum.ROLLBACKED,
            )
        )
        transactions = result.scalars().all()
        return sum(
            (to_usd(tx.amount, tx.currency) for tx in transactions),
            start=Decimal(0),
        )

    async def get_not_rollbacked_withdraw_amount(
        self, dt_gt: date, dt_lt: date
    ) -> Decimal:
        result = await self.session.execute(
            select(Transaction).where(
                func.date(Transaction.created) >= dt_gt,
                func.date(Transaction.created) <= dt_lt,
                Transaction.amount < 0,
                Transaction.status != TransactionStatusEnum.ROLLBACKED,
            )
        )
        transactions = result.scalars().all()
        return sum(
            (to_usd(tx.amount, tx.currency) for tx in transactions),
            start=Decimal(0),
        )

    async def get_transactions_count(self, dt_gt: date, dt_lt: date) -> int:
        result = await self.session.execute(
            select(func.count(Transaction.id)).where(
                func.date(Transaction.created) >= dt_gt,
                func.date(Transaction.created) <= dt_lt,
            )
        )
        return int(result.scalar() or 0)

    async def get_not_rollbacked_transactions_count(
        self, dt_gt: date, dt_lt: date
    ) -> int:
        result = await self.session.execute(
            select(func.count(Transaction.id)).where(
                func.date(Transaction.created) >= dt_gt,
                func.date(Transaction.created) <= dt_lt,
                Transaction.status != TransactionStatusEnum.ROLLBACKED,
            )
        )
        return int(result.scalar() or 0)
