from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import User, CharityProject
from app.schemas.schemas import DonationCreate, MyDonationDB, AllDonationDB
from app.services import free_funds_transfer

router = APIRouter()


@router.get(
    '/',
    response_model=List[AllDonationDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
) -> List[AllDonationDB]:
    """
    Только для суперюзеров.
    Возвращает список всех пожертвований.
    """
    return await donation_crud.get_multi(session)


@router.post(
    '/',
    response_model=MyDonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
) -> MyDonationDB:
    """Сделать пожертвование."""
    funds_from_donation = await free_funds_transfer(
        amount=donation.full_amount,
        model_to_recalculate_funds=CharityProject,
        session=session,
    )
    return await donation_crud.create(
        obj_in=donation,
        session=session,
        invested_amount=funds_from_donation,
        fully_invested=(funds_from_donation == donation.full_amount),
        close_date=(datetime.now() if funds_from_donation == donation.full_amount else None),
        user=user,
        # понимаю, что лишнее, уже есть в модели, но тесты хотят тут
        create_date=datetime.now(),
    )


@router.get(
    '/my/',
    response_model=List[MyDonationDB],
)
async def get_my_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
) -> List[AllDonationDB]:
    """Вернуть список пожертвований пользователя, выполняющего запрос."""
    return await donation_crud.get_by_user(
        session=session, user=user
    )
