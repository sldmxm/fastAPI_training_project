from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.project import project_crud
from app.models import CharityProject


async def check_project_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    if await project_crud.get_id_by_name(project_name, session):
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    project = await project_crud.get(
        project_id,
        session,
    )
    if not project:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    return project


async def check_project_before_delete(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    project = await check_project_exists(project_id, session)
    if project.invested_amount:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return project


async def check_project_before_edit(
        project_id: int,
        session: AsyncSession,
        full_amount: Optional[int] = None,
        **kwargs
) -> CharityProject:
    project = await check_project_exists(project_id, session)
    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )
    if full_amount and project.invested_amount > full_amount:
        raise HTTPException(
            status_code=422,
            detail='Нельзя установить требуемую сумму меньше уже вложенной!'
        )
    return project
