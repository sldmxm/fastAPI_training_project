from typing import List

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser

from app.crud.project import project_crud
from app.schemas.schemas import ProjectDuration
from app.services.google_api import (
    spreadsheets_create, spreadsheets_update_value, set_user_permissions
)

router = APIRouter()


@router.post(
    '/',
    response_model=List[ProjectDuration],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    """Только для суперюзеров."""
    projects = await project_crud.get_projects_by_completion_rate(
        session
    )
    if not projects:
        return []

    spreadsheet_id = await spreadsheets_create(wrapper_services)
    await set_user_permissions(spreadsheet_id, wrapper_services)
    await spreadsheets_update_value(spreadsheet_id,
                                    projects,
                                    wrapper_services)
    return [
        {'project': project, 'duration': str(duration)}
        for project, duration in projects
    ]
