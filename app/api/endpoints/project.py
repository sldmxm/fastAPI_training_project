from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import app.api.validators as validators
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.project import project_crud
from app.models import Donation
from app.schemas.schemas import ProjectCreate, ProjectDB, ProjectUpdate
from app.services import free_funds_transfer

router = APIRouter()


@router.post(
    '/',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def create_project(
        project: ProjectCreate,
        session: AsyncSession = Depends(get_async_session),
) -> ProjectDB:
    """Только для суперюзеров. Создаёт благотворительный проект."""
    await validators.check_project_name_duplicate(
        project.name, session
    )
    funds_for_project = await free_funds_transfer(
        amount=project.full_amount,
        model_to_recalculate_funds=Donation,
        session=session,
    )
    return await project_crud.create(
        obj_in=project,
        session=session,
        invested_amount=funds_for_project,
        fully_invested=(funds_for_project == project.full_amount),
        close_date=(datetime.now() if funds_for_project == project.full_amount else None),
        # понимаю, что лишнее, уже есть в модели, но тесты хотят тут
        create_date=datetime.now(),
    )


@router.get(
    '/',
    response_model=List[ProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
        session: AsyncSession = Depends(get_async_session),
) -> List[ProjectDB]:
    """Возвращает список всех проектов."""
    return await project_crud.get_multi(session)


@router.delete(
    '/{project_id}',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
) -> ProjectDB:
    """
    Только для суперюзеров.
    Удаляет проект.
    Нельзя удалить проект, в который уже были инвестированы
    средства, его можно только закрыть.
    """
    project = await validators.check_project_before_delete(
        project_id=project_id, session=session,
    )
    project = await project_crud.remove(project, session)
    return project


@router.patch(
    '/{project_id}',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
        project_id: int,
        project_update: ProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
) -> ProjectDB:
    """
    Только для суперюзеров.
    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    await validators.check_project_name_duplicate(
        project_update.name, session
    )
    project = await validators.check_project_before_edit(
        **project_update.dict(),
        project_id=project_id,
        session=session,
    )
    project = await project_crud.update(
        db_obj=project,
        obj_in=project_update,
        session=session,
    )
    return project
