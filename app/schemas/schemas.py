from datetime import datetime
from typing import Optional, TypedDict

from pydantic import BaseModel, Extra, Field
from pydantic.class_validators import validator
from pydantic.types import PositiveInt

from app.core.config import settings


class ProjectBase(BaseModel):
    name: Optional[str]
    description: Optional[str]
    full_amount: Optional[PositiveInt]

    class Config:
        extra = Extra.forbid


class ProjectCreate(ProjectBase):
    name: str = Field(
        ...,
        min_length=1,
        max_length=settings.project_name_length,
    )
    description: str = Field(..., min_length=1)
    full_amount: PositiveInt


class ProjectUpdate(ProjectBase):
    @validator('name', 'description')
    def name_length_check(cls, value: str):
        if not value:
            raise ValueError('Значение не должно быть пустым.')
        return value


class ProjectDB(ProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True


class ProjectDuration(TypedDict):
    project: ProjectDB
    duration: str


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class MyDonationDB(DonationCreate):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class AllDonationDB(MyDonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
