from sqlalchemy import (
    Column, String, Text
)

from .abstract import ProjectAndDonationAbstractModel
from app.core.config import settings


class CharityProject(ProjectAndDonationAbstractModel):
    name = Column(
        String(settings.project_name_length),
        unique=True,
        nullable=False
    )
    description = Column(Text, nullable=False)

    def __str__(self):
        return f'<Project {self.name}>'

    def __repr__(self):
        return f'<Project {self.name} - {self.description}>'
