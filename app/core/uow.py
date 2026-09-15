from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analysis import AnalysisRepository
from app.repositories.transactions import TransactionRepository
from app.repositories.user import UserBalanceRepository, UserRepository


class UnitOfWork:
    """Unit of Work: one session -> one transaction for all repositories.

    Every repository is created from the same session, so changes made through
    different repositories are committed by a single ``commit()`` and rolled
    back by a single ``rollback()``. Services own the transaction boundary.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)
        self.balances = UserBalanceRepository(session)
        self.transactions = TransactionRepository(session)
        self.analysis = AnalysisRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
