from datetime import timedelta
from typing import Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDProject(CRUDBase):
    async def get_projects_by_completion_rate(
        self, session: AsyncSession
    ) -> list[Tuple[CharityProject, timedelta]]:
        projects = await session.execute(
            select(
                CharityProject,
                (func.strftime('%s', CharityProject.close_date) -
                 func.strftime('%s', CharityProject.create_date)
                 ).label('duration'),
            ).where(
                CharityProject.fully_invested
            ).order_by('duration')
        )
        projects = [
            (project, timedelta(seconds=duration))
            for project, duration in projects
        ]
        return projects


project_crud = CRUDProject(CharityProject)
