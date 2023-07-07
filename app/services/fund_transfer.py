from datetime import datetime
from typing import Type

from sqlalchemy import select, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import ProjectAndDonationAbstractModel


async def free_funds_transfer(
        amount: int,
        model_to_recalculate_funds: Type[ProjectAndDonationAbstractModel],
        session: AsyncSession,
) -> int:
    items_to_recalculate = await session.execute(
        select(model_to_recalculate_funds).where(
            not_(model_to_recalculate_funds.fully_invested)
        )
    )
    free_funds = 0
    for item in items_to_recalculate.scalars().all():
        free_funds += item.full_amount - item.invested_amount
        item.invested_amount = (item.full_amount -
                                max(0, free_funds - amount)
                                )
        item.fully_invested = item.invested_amount == item.full_amount
        item.close_date = (
            datetime.now() if item.fully_invested else None
        )
        session.add(item)
        if free_funds >= amount:
            break
    return min(free_funds, amount)
